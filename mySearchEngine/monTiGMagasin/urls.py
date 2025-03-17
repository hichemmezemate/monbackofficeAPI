from django.urls import path
from monTiGMagasin import views

urlpatterns = [
    path('infoproducts/', views.InfoProductList.as_view()),
    path('infoproduct/<int:tig_id>/', views.InfoProductDetail.as_view()),
    path('infoproducts/poissons', views.InfoProductListPoissons.as_view()),
    path('infoproducts/crustaces', views.InfoProductListCrustaces.as_view()),
    path('infoproducts/fruitsdemer', views.InfoProductListFruitsDeMer.as_view()),
    path('transactions/', views.TransactionsList.as_view()),
    path('resumeFinancier/', views.ResumeFinancierView.as_view()),
    path('resumeFinancier2/', views.ResumeFinancierView2.as_view())
]
