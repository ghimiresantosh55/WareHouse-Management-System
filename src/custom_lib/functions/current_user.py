# Get the user id request parameter passed from purchase_order_serializer
def get_created_by(context_with_request):
    request = context_with_request.get('request', None)
    if not request.user.is_anonymous:
        return request.user
    else:
        return ''
