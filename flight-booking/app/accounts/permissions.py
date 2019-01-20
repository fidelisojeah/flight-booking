
GROUPS = {
    'client': [
        ('accounts', 'retrieve_own_picture'),
        ('accounts', 'delete_own_picture'),
        ('accounts', 'update_own_picture'),
    ],
    'super_staff': [
        ('accounts', 'retrieve_own_picture'),
        ('accounts', 'delete_own_picture'),
        ('accounts', 'update_own_picture'),
        ('accounts', 'update_any_picture'),
        ('accounts', 'delete_any_picture'),
        ('accounts', 'retrieve_any_picture'),
    ]
}
