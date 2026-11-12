#!/usr/bin/env python3
"""Una prueba breve individual, con lectura informativa y apagado final."""
import argparse
import json
import time
from pathlib import Path

from leer_as5600_tca import AS5600Reader, SENSORS
from pca9685_seguro import PCA9685Seguro


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--channel', type=int, choices=(0, 1, 2, 4, 8), default=4)
    parser.add_argument('--pulse-us', type=int, default=1500)
    parser.add_argument('--duration', type=float, default=0.2)
    args = parser.parse_args()
    if not 1450 <= args.pulse_us <= 1550 or not 0.1 <= args.duration <= 2.0:
        parser.error('Esta fase admite 1450..1550 us y 0.1..2.0 s')
    log = Path(__file__).resolve().parents[1] / 'datos' / 'pulsos_observados.jsonl'
    log.parent.mkdir(parents=True, exist_ok=True)
    # CH1 y CH8 identificados por observación física del operador.
    joint = {0: 'front_right_coxa_joint', 1: 'rear_right_coxa_joint',
             2: 'rear_right_coxa_joint', 4: 'front_right_femur_joint',
             8: 'front_left_coxa_joint'}[args.channel]
    record = dict(timestamp_ns=time.time_ns(), channel=args.channel,
                  joint=joint, pulse_us=args.pulse_us,
                  duration_s=args.duration, observation_pending=True)
    record['sensor_binding'] = ('operator_observed_channel' if args.channel in (1, 8)
                                else 'declared_map_requires_physical_confirmation')
    reader = None
    controller = None
    sensor = next(s for s in SENSORS if s.joint == record['joint'])
    try:
        reader = AS5600Reader(1)
        reader.disable_all()
        record['before'] = reader.read_sensor(sensor)
        controller = PCA9685Seguro()
        controller.arm()
        print(f'CH{args.channel}: {args.pulse_us} us durante {args.duration} s', flush=True)
        controller.set_pulse_us(args.channel, args.pulse_us)
        time.sleep(args.duration)
        controller.all_off()
        record['after'] = reader.read_sensor(sensor)
        record['completed'] = True
    except BaseException as error:
        record['error'] = str(error)
        raise
    finally:
        try:
            if controller is not None:
                controller.close()
        finally:
            if reader is not None:
                reader.close()
            with log.open('a', encoding='utf-8') as output:
                output.write(json.dumps(record) + '\n')
    print(json.dumps(record), flush=True)
    print('PWM apagado; falta observación del operador.', flush=True)


if __name__ == '__main__':
    main()
