from django.shortcuts import render

def buildings_overview(request):
    return render(request, 'buildings/overview.html')

def build_structure(request, region_id):
    return render(request, 'buildings/build.html')

def manage_building(request, building_id):
    return render(request, 'buildings/manage.html')
