ONBOARDING_STEPS = {
    'landlord': {
        1: 'Add profile details',
        2: 'Add first property',
        3: 'Complete onboarding',
    },
    'agent': {
        1: 'Add profile details',
        2: 'Add first property',
        3: 'Complete onboarding',
    },
    'tenant': {
        1: 'Set preferences',
        2: 'Complete onboarding',
    },
}

NIGERIAN_STATES = (
    ('abia', 'Abia'),
    ('adamawa', 'Adamawa'),
    ('akwa_ibom', 'Akwa Ibom'),
    ('anambra', 'Anambra'),
    ('bauchi', 'Bauchi'),
    ('bayelsa', 'Bayelsa'),
    ('benue', 'Benue'),
    ('borno', 'Borno'),
    ('cross_river', 'Cross River'),
    ('delta', 'Delta'),
    ('ebonyi', 'Ebonyi'),
    ('edo', 'Edo'),
    ('ekiti', 'Ekiti'),
    ('enugu', 'Enugu'),
    ('gombe', 'Gombe'),
    ('imo', 'Imo'),
    ('jigawa', 'Jigawa'),
    ('kaduna', 'Kaduna'),
    ('kano', 'Kano'),
    ('katsina', 'Katsina'),
    ('kebbi', 'Kebbi'),
    ('kogi', 'Kogi'),
    ('kwara', 'Kwara'),
    ('lagos', 'Lagos'),
    ('nasarawa', 'Nasarawa'),
    ('niger', 'Niger'),
    ('ogun', 'Ogun'),
    ('ondo', 'Ondo'),
    ('osun', 'Osun'),
    ('oyo', 'Oyo'),
    ('plateau', 'Plateau'),
    ('rivers', 'Rivers'),
    ('sokoto', 'Sokoto'),
    ('taraba', 'Taraba'),
    ('yobe', 'Yobe'),
    ('zamfara', 'Zamfara'),
    ('fct', 'Federal Capital Territory (FCT)'),
)

PROPERTY_TYPE_CHOICES = (
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('condo', 'Condo'),
        ('townhouse', 'Townhouse'),
        ('duplex', 'Duplex'),
        ('studio', 'Studio'),
        ('villa', 'Villa'),
        ('self_contained', 'Self Contained'),
        ('room and parlour', 'Room and Parlour'),
        ('shared accommodation', 'Shared Accommodation'),
        ('office space', 'Office Space'),
        ('commercial property', 'Commercial Property'),
        ('land', 'Land'),
    )

INTERVAL_CHOICES = (
    ('month', 'Month'),
    ('year', 'Year'),
)

COUNTRY_CHOICES = (
    ('nigeria', 'Nigeria'),
)

USER_TYPE_CHOICES = (
        ('landlord', 'Landlord'),
        ('tenant', 'Tenant'),
        ('agent', 'Agent'),
    )

SUPER_USER_TYPE_CHOICES = (
        ('landlord', 'Landlord'),
        ('agent', 'Agent'),
    )