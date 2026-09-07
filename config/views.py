from django.http import JsonResponse


def main(request):
    return JsonResponse({
        "status": "success",
        "message": "server is running",
    })