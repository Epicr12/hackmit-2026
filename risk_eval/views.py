from django.shortcuts import render


def risk_page(request):
    return render(request, "risk_eval/risk.html")
