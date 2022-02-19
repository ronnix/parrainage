def test_user_detail_url():
    from django.core.urlresolvers import reverse

    assert reverse('user-detail', args=["AvecMajuscules"]) == "/user/AvecMajuscules/"
