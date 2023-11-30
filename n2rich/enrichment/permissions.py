def has_perm(request, obj):
    if obj.is_active and obj.shareable == 'public':
        return True
    elif not request.user.is_authenticated:
        return False
    elif obj.user != request.user:
        return False
    else:
        return True