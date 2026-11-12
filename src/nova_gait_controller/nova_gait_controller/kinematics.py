"""Kinematics for the provisional NovaSM3 URDF leg geometry.

The formulation follows the same geometric approach used by mike4192's MIT
licensed spot_micro_kinematics_python project, adapted to this project's ROS
axis convention and measured/published NovaSM3 link lengths.
"""

from math import acos, atan2, cos, hypot, isfinite, log, pi, sin, sqrt


# Measured/reference NovaSM3 geometry. These values are shared by the
# kinematics, the 3D pose app and the simulation-training environments.
HIP_SPACING_X = 0.180  # distance between front and rear hip pivots
HIP_SPACING_Y = 0.120  # distance between left and right hip pivots
BODY_LENGTH = 0.230
BODY_WIDTH = 0.120
BODY_HEIGHT = 0.075

# Measured physical leg segments: coxa 1.5 in, femur 4.25 in, tibia 5.35 in.
COXA_LENGTH = 0.0381
FEMUR_LENGTH = 0.10795  # 4.25 in measured
TIBIA_LENGTH = 0.13589  # 5.35 in measured


def crawl_sample_profile(local_sample, samples_per_leg):
    """Return the transfer, swing progress and named crawl subphase."""
    if samples_per_leg < 4:
        raise ValueError('cada pata necesita al menos cuatro muestras')
    if not 0 <= local_sample < samples_per_leg:
        raise ValueError('muestra local fuera del cuarto de ciclo')

    transfer_values = [sin(pi * index / (samples_per_leg - 1))
                       for index in range(samples_per_leg)]
    transfer = transfer_values[local_sample] / max(transfer_values)
    if local_sample == 0:
        return transfer, 0.0, 'transfer_start', True
    if local_sample == 1:
        return transfer, 0.0, 'preload', True

    swing_progress = (local_sample - 1) / (samples_per_leg - 2)
    if local_sample == samples_per_leg - 1:
        return transfer, 1.0, 'touchdown', True
    if local_sample == 2:
        subphase = 'liftoff'
    elif local_sample == samples_per_leg - 2:
        subphase = 'landing'
    else:
        subphase = 'flight'
    return transfer, swing_progress, subphase, False


def crawl_swing_height(progress, subphase, landing_height_ratio,
                       liftoff_height_ratio=2 ** -0.5):
    """Return normalized lift with independently tunable ascent and descent.

    ``landing_height_ratio`` retains its original, directly observable meaning:
    it is the normalized height at 75 percent swing progress.  Instead of
    replacing only the discrete ``landing`` sample, it now determines a power
    curve from the apex to touchdown. A smaller ratio advances the descent and
    a larger ratio sustains lift for longer. ``liftoff_height_ratio`` is the
    normalized height at 25 percent swing progress: values above the nominal
    sine value accelerate early clearance without changing the zero or apex.
    """
    if not 0.0 <= progress <= 1.0:
        raise ValueError('progreso de oscilación fuera de [0, 1]')
    if not 0.0 <= landing_height_ratio <= 1.0:
        raise ValueError('landing_height_ratio debe estar entre 0 y 1')
    if not 0.0 <= liftoff_height_ratio <= 1.0:
        raise ValueError('liftoff_height_ratio debe estar entre 0 y 1')
    if progress <= 0.5:
        if liftoff_height_ratio == 0.0:
            return 0.0 if progress < 0.5 else 1.0
        if liftoff_height_ratio == 1.0:
            return 0.0 if progress == 0.0 else 1.0
        if liftoff_height_ratio != 2 ** -0.5:
            ascent_progress = progress / 0.5
            exponent = log(liftoff_height_ratio) / log(0.5)
            return ascent_progress ** exponent
        return sin(pi * progress)
    if landing_height_ratio == 0.0:
        return 0.0
    if landing_height_ratio == 1.0:
        return 1.0 if progress < 1.0 else 0.0

    descent_progress = (progress - 0.5) / 0.5
    exponent = log(landing_height_ratio) / log(0.5)
    return (1.0 - descent_progress) ** exponent


def forward_leg(q_coxa, q_femur, q_tibia, side):
    """Return foot (x, y, z) relative to a hip pivot in the body frame."""
    x = (-FEMUR_LENGTH * sin(q_femur)
         - TIBIA_LENGTH * sin(q_femur + q_tibia))
    planar_z = (-FEMUR_LENGTH * cos(q_femur)
                - TIBIA_LENGTH * cos(q_femur + q_tibia))
    angle = side * q_coxa
    lateral = side * COXA_LENGTH
    y = cos(angle) * lateral - sin(angle) * planar_z
    z = sin(angle) * lateral + cos(angle) * planar_z
    return x, y, z


def inverse_leg(x, y, z, side):
    """Return URDF (coxa, femur, tibia) angles for a reachable foot target."""
    radial_sq = y * y + z * z - COXA_LENGTH * COXA_LENGTH
    if radial_sq < -1e-10:
        raise ValueError('Objetivo dentro del radio de la coxa')
    planar_z = -sqrt(max(0.0, radial_sq))

    coxa_rotation = atan2(z, y) - atan2(planar_z, side * COXA_LENGTH)
    q_coxa = atan2(sin(coxa_rotation), cos(coxa_rotation)) / side

    down = -planar_z
    backward = -x
    cosine_knee = ((down * down + backward * backward
                    - FEMUR_LENGTH * FEMUR_LENGTH - TIBIA_LENGTH * TIBIA_LENGTH)
                   / (2.0 * FEMUR_LENGTH * TIBIA_LENGTH))
    if cosine_knee < -1.0 - 1e-9 or cosine_knee > 1.0 + 1e-9:
        raise ValueError('Objetivo fuera del alcance fémur-tibia')
    cosine_knee = max(-1.0, min(1.0, cosine_knee))
    q_tibia = -acos(cosine_knee)
    q_femur = (atan2(backward, down)
               - atan2(TIBIA_LENGTH * sin(q_tibia),
                       FEMUR_LENGTH + TIBIA_LENGTH * cos(q_tibia)))

    result = (q_coxa, q_femur, q_tibia)
    if not all(isfinite(value) for value in result):
        raise ValueError('Solución cinemática no finita')
    if not (-0.60 <= q_coxa <= 0.60
            and -1.20 <= q_femur <= 1.20
            and -2.20 <= q_tibia <= 0.10):
        raise ValueError(f'Solución fuera de límites articulares: {result}')
    return result


def cartesian_crawl(stand, samples=24, step_length=0.018, step_height=0.014,
                    lateral_shift=0.004, fore_aft_shift=0.008,
                    front_landing_height_ratio=2 ** -0.5,
                    rear_landing_height_ratio=2 ** -0.5,
                    rear_liftoff_height_ratio=2 ** -0.5,
                    rear_swing_height_scale=1.0,
                    preload_shift_scale=1.0):
    """Generate a quasi-static crawl with explicit weight transfer.

    The common Cartesian shifts move the trunk away from the leg that is about
    to swing: laterally toward the opposite side and longitudinally toward the
    opposite axle.  They vanish at quarter-cycle boundaries, so the gait stays
    continuous and periodic without changing step length or lift height.
    """
    if samples < 16 or samples > 80 or samples % 4:
        raise ValueError('samples debe ser múltiplo de 4 entre 16 y 80')
    if not 0.002 <= step_length <= 0.040:
        raise ValueError('step_length debe estar entre 0,002 y 0,040 m')
    if not 0.004 <= step_height <= 0.030:
        raise ValueError('step_height debe estar entre 0,004 y 0,030 m')
    if not 0.0 <= lateral_shift <= 0.015:
        raise ValueError('lateral_shift debe estar entre 0 y 0,015 m')
    if not 0.0 <= fore_aft_shift <= 0.015:
        raise ValueError('fore_aft_shift debe estar entre 0 y 0,015 m')
    if not 0.0 <= front_landing_height_ratio <= 1.0:
        raise ValueError('front_landing_height_ratio debe estar entre 0 y 1')
    if not 0.0 <= rear_landing_height_ratio <= 1.0:
        raise ValueError('rear_landing_height_ratio debe estar entre 0 y 1')
    if not 0.0 <= rear_liftoff_height_ratio <= 1.0:
        raise ValueError('rear_liftoff_height_ratio debe estar entre 0 y 1')
    if not 0.5 <= rear_swing_height_scale <= 1.5:
        raise ValueError('rear_swing_height_scale debe estar entre 0,5 y 1,5')
    if not 1.0 <= preload_shift_scale <= 2.0:
        raise ValueError('preload_shift_scale debe estar entre 1 y 2')

    neutral = {
        'fl': forward_leg(*stand, side=1),
        'fr': forward_leg(*stand, side=-1),
        'rl': forward_leg(*stand, side=1),
        'rr': forward_leg(*stand, side=-1),
    }
    # Phase offsets produce swing order FL, RR, FR, RL.
    offsets = {'fl': 0.75, 'rr': 0.50, 'fr': 0.25, 'rl': 0.00}
    sides = {'fl': 1, 'fr': -1, 'rl': 1, 'rr': -1}
    order = ('fl', 'rr', 'fr', 'rl')
    duty = 0.75
    poses = []
    samples_per_leg = samples // 4
    for sample in range(samples):
        cycle = sample / samples
        quarter = min(3, int(cycle * 4.0))
        local_sample = sample % samples_per_leg
        swing_leg = order[quarter]
        transfer_profile, _, _, _ = crawl_sample_profile(
            local_sample, samples_per_leg)
        if local_sample in (1, 2):
            transfer_profile *= preload_shift_scale
        common_y = (1.0 if swing_leg in ('fl', 'rl') else -1.0) \
            * lateral_shift * transfer_profile
        # A negative foot-frame shift corresponds to moving the trunk forward.
        common_x = (-1.0 if swing_leg in ('rl', 'rr') else 1.0) \
            * fore_aft_shift * transfer_profile
        legs = {}
        for name in ('fl', 'fr', 'rl', 'rr'):
            phase = (cycle + offsets[name]) % 1.0
            x0, y0, z0 = neutral[name]
            if phase < duty:  # stance: foot moves backward under the body
                progress = phase / duty
                x = x0 + step_length * (0.5 - progress)
                z = z0
            else:  # swing: smooth forward return with a parabolic lift
                swing_sample = int(round((phase - duty) * samples))
                _, progress, subphase, _ = crawl_sample_profile(
                    swing_sample, samples_per_leg)
                x = x0 + step_length * (-0.5 + progress)
                landing_ratio = (front_landing_height_ratio
                                 if name in ('fl', 'fr')
                                 else rear_landing_height_ratio)
                liftoff_ratio = (2 ** -0.5 if name in ('fl', 'fr')
                                 else rear_liftoff_height_ratio)
                height_scale = (rear_swing_height_scale
                                if name in ('rl', 'rr') else 1.0)
                z = z0 + step_height * height_scale * crawl_swing_height(
                    progress, subphase, landing_ratio, liftoff_ratio)
            legs[name] = inverse_leg(
                x + common_x, y0 + common_y, z, sides[name])
        poses.append([*legs['fl'], *legs['fr'], *legs['rl'], *legs['rr']])
    return poses


def cartesian_step_walk(stand, samples=48, step_length=0.016,
                        step_height=0.008, weight_shift=0.004,
                        fore_aft_shift=0.0):
    """Generate a conservative walk with explicit lateral weight transfer.

    Each quarter-cycle belongs to one leg in FL, RR, FR, RL order.  A smooth
    lateral shift moves the body away from the swing leg.  The foot remains in
    stance for 75 percent of the full cycle and swings for 25 percent.
    """
    if samples < 16 or samples > 96 or samples % 8:
        raise ValueError('step_samples debe ser múltiplo de 8 entre 16 y 96')
    if not 0.002 <= step_length <= 0.035:
        raise ValueError('step_length debe estar entre 0,002 y 0,035 m')
    if not 0.004 <= step_height <= 0.025:
        raise ValueError('step_height debe estar entre 0,004 y 0,025 m')
    if not 0.0 <= weight_shift <= 0.015:
        raise ValueError('step_weight_shift debe estar entre 0 y 0,015 m')
    if not 0.0 <= fore_aft_shift <= 0.015:
        raise ValueError('step_fore_aft_shift debe estar entre 0 y 0,015 m')

    neutral = {
        'fl': forward_leg(*stand, side=1),
        'fr': forward_leg(*stand, side=-1),
        'rl': forward_leg(*stand, side=1),
        'rr': forward_leg(*stand, side=-1),
    }
    sides = {'fl': 1, 'fr': -1, 'rl': 1, 'rr': -1}
    order = ('fl', 'rr', 'fr', 'rl')
    offsets = {'fl': 0.75, 'rr': 0.50, 'fr': 0.25, 'rl': 0.00}
    duty = 0.75
    poses = []

    for sample in range(samples):
        cycle = sample / samples
        quarter = min(3, int(cycle * 4.0))
        local_quarter = cycle * 4.0 - quarter
        swing_leg = order[quarter]
        # Positive foot shift means the trunk moves to the right, away from a
        # left swing leg; the sign reverses for a right swing leg.
        shift_sign = 1.0 if swing_leg in ('fl', 'rl') else -1.0
        lateral_shift = shift_sign * weight_shift * sin(pi * local_quarter)
        # Descargar el eje de la pata oscilante: los objetivos de los pies se
        # desplazan hacia atrás para mover el tronco hacia delante al liberar
        # una pata trasera, y viceversa para una pata delantera.
        fore_aft_sign = 1.0 if swing_leg in ('fl', 'fr') else -1.0
        longitudinal_shift = (
            fore_aft_sign * fore_aft_shift * sin(pi * local_quarter))
        legs = {}

        for name in ('fl', 'fr', 'rl', 'rr'):
            phase = (cycle + offsets[name]) % 1.0
            x0, y0, z0 = neutral[name]
            if phase < duty:
                progress = phase / duty
                x = x0 + step_length * (0.5 - progress)
                z = z0
            else:
                # Include touchdown in the final discrete swing sample; using
                # the continuous denominator would stop at 75 % for 32 samples
                # and create a discontinuity on return to stance.
                swing_span = (1.0 - duty) - 1.0 / samples
                progress = min(1.0, (phase - duty) / swing_span)
                x = x0 + step_length * (-0.5 + progress)
                z = z0 + step_height * 4.0 * progress * (1.0 - progress)
            legs[name] = inverse_leg(
                x + longitudinal_shift, y0 + lateral_shift, z, sides[name])
        poses.append([*legs['fl'], *legs['fr'], *legs['rl'], *legs['rr']])
    return poses
