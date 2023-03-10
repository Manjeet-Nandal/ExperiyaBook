from django.urls import path,re_path
from bima_policy.models import *
from .views import *
app_name='bima_policy'
urlpatterns = [
    path('login/', loginView, name='login'),
    path('logout/', logout, name='logout'),
    path('profile/',Profile,name='profile'),
    path('dashboard/',dashboard , name='dashboard'),
    path('profile/bank_details/',bank_details,name='bank_det'),  
    path('profile/bank_details/<str:id>',delete_bank_details,name='del_bank'),
    path('user/',staffmanage, name='staff'),
    path('user/edit/<str:id>',staff_edit,name='staff_edit'),
    path('agent/',agent, name='agent'),
    path('agent/add_agent/',add_agent, name='add_agent'),
    path('agent/profile',agent_profile , name='agent_profile'),
    path('service_provider/', service_provider, name='service_p'),
    path('service_provider/add_sp/', add_sp, name='add_sp'),
    path('service_provider/<str:id>/delete', delete_sp, name='del_sp'),
    path('service_provider/<str:id>/edit', edit_sp, name='edit_sp'),
    path('service_provider/broker/<str:id>/del',del_broker_code, name='del_broker_code'),
    path('vehicle/',vehicle_view, name='vehi'),
    path('vehicle/<str:id>',delete_vehicle,name='del_vehicle'),
    path('vehicle/<str:id>/edit',edit_vehicle,name='edit_vehicle'),
    path('insurance_comp/', ins_comp, name="ins_comp"),
    path('insurance_comp/<str:id>',ins_del, name='ins_del'),
    path('rto/',rto_list , name="rto"),
    path('rto/<str:id>',update_rto, name='rto_delete'),
    path('slab/', slab, name="slab"),
    path('slab/<str:id>',slab_delete,name="del_slab"),
    path('slab/<str:id>/edit',slab_edit,name="edit_slab"),
    path('slab/slab_payoutlist/<str:id>', slab_payout, name="slab_payout"),
    path('slab/slab_payoutform/',slab_payoutform, name="slab_payoutform"),
    path('slab/slab_payoutformshow/<str:id>',slab_payoutformshow, name="slab_payoutformshow"),
    path('slab/slab_payoutlist/payout/<str:id>/delete',payout_delete, name="payout_delete"),
    path('slab/slab_payoutlist/payout/<str:id>/edit',payout_edit, name="payout_edit"),
    path('policy/',create_policy.as_view(), name="create_policy"),
    path('policy/create_policy_non_motor',create_policy_non_motor.as_view(), name="create_policy_non_motor"),
    path('policy/entry',policy_entry, name="policy_entry"),
    path('policy/policy_entrydata/<str:id>',policy_entrydata, name="update"),
    path('policy/<str:id>/delete',policy_delete, name="policy_delete"),
    path('policy/edit/<str:id>', edit_policy,name="edit_policy"),
    path('policy/import',policy_import, name="policy_import"),
    path('policy/save/<str:id>',apply_policy, name="apply_policy"),  
    path('upcomingRenewal/',upcoming_renewal, name="upcoming_renewal"),
    path('agent_payable/',agentpayable, name="agentpayable"),
    path('agent_statement/',agent_statement, name="agent_statement"),
    path('SP_receive/',sp_receivable, name="sp_receivable"),
    path('SP_statement/',sp_statement, name="sp_statement"),
    path('report_agent/',report_agent, name="report_agent"),
    path('report_PP/',report_policyprovider, name="report_policyprovider"),
    path('report_Vcat/',report_vehicleCategory, name="report_vehicleCategory"),
    path('report_broker/',report_brokercode, name="report_brokercode"),
    path('report_insurance/',report_insurance_comp, name="report_insurance_comp"),
    path('subscription/',subscription, name="subscription"),
]