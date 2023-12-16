from django.urls import path
from . import views

# define all routes
urlpatterns = [
    path('checkAdminToken', views.checkAdminToken, name='checkAdminToken'),
    path('adminLogin', views.adminLogin, name='adminLogin'),
    path('createUser', views.createUser, name='createUser'),
    path('deleteUserById', views.deleteUserById, name="deleteUserById"),
    path('updateUserById/<str:uid>', views.updateUserById, name="updateUserById"),
    path('issueInvitationCode', views.issueInvitationCode, name="issueInvitationCode"),
    path('getAllUserInfo', views.getAllUserInfo, name="getAllUserInfo"),
    path('getAllInvitationCode', views.getAllInvitationCode, name="getAllInvitationCode"),
    path('deleteInvitationCode', views.deleteInvitationCode, name="deleteInvitationCode"),
    path('getQARecordsByPage', views.getQARecordsByPage, name="getQARecordsByPage"),
    path('deleteQARecordsBySku/<str:sku>', views.deleteQARecordsBySku, name="deleteQARecordsBySku"),
]
