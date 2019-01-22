
GROUPS = {
    'client': [
        ('accounts', 'retrieve_own_picture'),
        ('accounts', 'delete_own_picture'),
        ('accounts', 'update_own_picture'),

        ('airline', 'view_flights'),

        ('flight', 'view_flight'),

        ('airport', 'view_airport'),

        ('reservation', 'update_own_reservation'),
        ('reservation', 'delete_own_reservation'),
        ('reservation', 'retrieve_own_reservations'),
        ('reservation', 'add_reservation'),
    ],
    'staff': [
        ('accounts', 'retrieve_own_picture'),
        ('accounts', 'delete_own_picture'),
        ('accounts', 'update_own_picture'),

        ('airline', 'add_flights'),
        ('airline', 'view_flights'),
        ('airline', 'change_flights'),
        ('airline', 'delete_flights'),

        ('flight', 'view_flight'),
        ('flight', 'add_flight'),
        ('flight', 'change_flight'),
        ('flight', 'delete_flight'),

        ('airport', 'view_airport'),
        ('airport', 'change_airport'),

        ('airline', 'view_airline'),
        ('airline', 'change_airline'),
    ],
    'super_staff': [
        ('reservation', 'update_any_reservations'),
        ('reservation', 'delete_any_reservations'),
        ('reservation', 'retrieve_any_reservations'),
        ('reservation', 'create_any_reservation'),

        ('accounts', 'update_any_picture'),
        ('accounts', 'delete_any_picture'),
        ('accounts', 'retrieve_any_picture'),

        ('airline', 'add_flights'),
        ('airline', 'change_flights'),
        ('airline', 'delete_flights'),
        ('airline', 'view_flights'),

        ('flight', 'view_flight'),
        ('flight', 'add_flight'),
        ('flight', 'change_flight'),
        ('flight', 'delete_flight'),

        ('airline', 'add_airline'),
        ('airline', 'delete_airline'),
        ('airport', 'view_airport'),
        ('airport', 'change_airport'),

        ('airport', 'add_airport'),
        ('airport', 'delete_airport'),
        ('airline', 'view_airline'),
        ('airline', 'change_airline'),
    ]
}
