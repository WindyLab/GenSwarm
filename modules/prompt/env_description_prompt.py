ENV_DES = '''
Environment:
    bounds:{'x_min': -5.0, 'x_max': 5.0, 'y_min': -5.0, 'y_max': 5.0}
    
Robot:
    radius: 0.2m (with a circular shape)
    max_speed: 1m/s
    Control Method: Omnidirectional speed control
    Initial position: random
    Initial speed: np.array([0, 0])
'''.strip()
