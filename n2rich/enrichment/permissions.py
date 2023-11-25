def has_perm(request, obj):
    if obj.shareable == 'public' and obj.is_active:
        return True
    elif not obj.is_active:
        return False
    elif not request.user.is_authenticated:
        return False
    elif obj.user != request.user:
        return False
    else:
        return True