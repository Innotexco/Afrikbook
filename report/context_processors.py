def pdf_template(request):
    """Makes pdf_template available in every template automatically."""
    if not request.user.is_authenticated:
        return {'pdf_template': 'classic'}
    try:
        db      = request.user.company_id.db_name
        profile = CreateProfile.objects.using(db).get(
            CompanyName=request.user.company_id.company_name
        )
        return {'pdf_template': profile.pdf_template or 'classic'}
    except Exception:
        return {'pdf_template': 'classic'}
