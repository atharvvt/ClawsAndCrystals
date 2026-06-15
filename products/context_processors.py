from .compare import get_compare_ids


def compare_context(request):
    compare_ids = get_compare_ids(request)
    return {
        "compare_count": len(compare_ids),
        "compare_ids": compare_ids,
    }
