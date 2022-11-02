from django.views.generic.base import TemplateView
import random

class HomePageView(TemplateView):
    my_list = [1, 2, 3, 4, 5, 6]
    rand_num = random.choice(my_list)
    html = "Random Number: %s" % rand_num
    template_name = "index.html"