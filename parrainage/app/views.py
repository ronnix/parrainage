import csv

from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Case, Count, Max, When
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.http import HttpResponseNotFound, HttpResponse
from django.utils.decorators import method_decorator
from django.utils.http import urlencode
from django.views.generic import TemplateView, ListView, DetailView, View

from parrainage.app.models import Elu, User, UserSettings


def global_context(request):
    return {
        "candidature": settings.NOM_CANDIDATURE,
    }


def make_options(choices, current):
    return [
        (
            value,
            label,
            " selected" if current == str(value) else "",
            " disabled" if label.startswith("-") else "",
        )
        for value, label in choices
    ]


def get_assigned_elus(user, exclude_finished=True):
    if exclude_finished:
        qs = user.elu_set.filter(status__lt=Elu.STATUS_REFUSED)
    else:
        qs = user.elu_set.all()
    return qs.annotate(last_updated=Max("notes__timestamp")).order_by(
        "status", "last_updated"
    )


def get_department_options(request):
    return make_options(
        [(str(dpt), str(dpt)) for dpt in get_department_list(request)],
        get_default_department(request),
    )


def get_department_list(request):
    departments = set(
        Elu.objects.only("department")
        .exclude(department="")
        .values_list("department", flat=True)
        .distinct()
        .order_by("department")
    )
    if (
        request.user.is_authenticated()
        and hasattr(request.user, "settings")
        and request.user.settings.department
    ):
        departments.add(request.user.settings.department)
    return list(sorted(departments))


def get_default_department(request):
    settings = getattr(request.user, "settings", None)
    if settings and settings.department:
        return settings.department
    return "01"


def get_department_data():
    stats = {}

    # Loop over (department, status)
    values = Elu.objects.values("department", "status").annotate(Count("id"))
    for data in values:
        department = display_department = data["department"]
        if len(display_department) == 1:
            display_department = "0" + department
        status = data["status"]
        count = data["id__count"]
        dep_stats = stats.setdefault(
            department,
            {
                "department": department,
                "display_department": display_department,
                "count_elus": 0,
                "count_nothing": 0,
                "count_accepted": 0,
                "count_blocked": 0,
                "count_refused": 0,
                "count_contacted": 0,
                "count_to_contact": 0,
                "count_users": 0,
                "user_list": [],
            },
        )
        dep_stats["count_elus"] += count
        if status == Elu.STATUS_NOTHING:
            dep_stats["count_nothing"] += count
        elif status == Elu.STATUS_CONTACTED:
            dep_stats["count_contacted"] += count
        elif status == Elu.STATUS_TO_CONTACT or status == Elu.STATUS_TO_CONTACT_TEAM:
            dep_stats["count_to_contact"] += count
        elif status == Elu.STATUS_BLOCKED:
            dep_stats["count_blocked"] += count
        elif status == Elu.STATUS_REFUSED:
            dep_stats["count_refused"] += count
        elif status >= Elu.STATUS_ACCEPTED:
            dep_stats["count_accepted"] += count

    # Loop over all users
    users = User.objects.select_related("settings").order_by("username")
    for user in users:
        if not hasattr(user, "settings"):
            continue
        department = user.settings.department
        stats[department]["count_users"] += 1
        stats[department]["user_list"].append(user)

    return stats


def redirect_by_city_code(request, city_code):
    city_code = city_code.lstrip("0")
    elu = Elu.objects.filter(city_code=city_code).first()
    city_name = request.GET.get("city_name")
    if elu:
        redirect_url = elu.get_absolute_url()
    elif city_name:
        redirect_url = reverse("elu-list") + "?" + urlencode({"search": city_name})
    else:
        return HttpResponseNotFound("<h1>Unknown city code</h1>")
    return HttpResponseRedirect(redirect_url)


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            context["departements"] = get_department_options(self.request)
            context["user_count"] = User.objects.count()
            context["elus_contacted"] = Elu.objects.filter(
                status__gt=Elu.STATUS_NOTHING
            ).count()
            context["elus_refused"] = Elu.objects.filter(
                status=Elu.STATUS_REFUSED
            ).count()
            context["elus_accepted"] = Elu.objects.filter(
                status__gte=Elu.STATUS_ACCEPTED
            ).count()
            context["elus_responded"] = (
                context["elus_refused"] + context["elus_accepted"]
            )
            context["elus_in_process"] = (
                context["elus_contacted"] - context["elus_responded"]
            )
            context["my_elus"] = get_assigned_elus(self.request.user)
        return context


class EluListView(ListView):
    template_name = "elu-list.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["departments"] = self.get_departements_choices()
        context["statuses"] = self.get_status_choices()
        context["sort_keys"] = self.get_sort_keys()
        return context

    def get_departements_choices(self):
        choices = [
            ("tous", "Tous les départements"),
            ("", "---"),
        ] + [(str(dpt), str(dpt)) for dpt in get_department_list(self.request)]
        return make_options(choices, self.request.GET.get("department"))

    def get_status_choices(self):
        choices = [
            ("", "Tous les statuts"),
            ("", "---"),
            (
                ",".join(
                    map(
                        str,
                        [
                            Elu.STATUS_NOTHING,
                            Elu.STATUS_CONTACTED,
                            Elu.STATUS_TO_CONTACT,
                            Elu.STATUS_TO_CONTACT_TEAM,
                            Elu.STATUS_BLOCKED,
                        ],
                    )
                ),
                "En cours",
            ),
            (
                ",".join(
                    map(
                        str,
                        [
                            Elu.STATUS_REFUSED,
                            Elu.STATUS_ACCEPTED,
                            Elu.STATUS_RECEIVED,
                        ],
                    )
                ),
                "Terminés",
            ),
            ("", "---"),
        ] + list(Elu._meta.get_field("status").choices)
        return make_options(choices, self.request.GET.get("status"))

    def get_sort_keys(self):
        return make_options(
            [
                ("city", "Nom de la commune"),
                ("", "Nom de l’élu"),
                ("priority", "Priorité"),
                ("status", "Statut"),
            ],
            self.request.GET.get("sort"),
        )

    def get_queryset(self):
        qs = Elu.objects.all()
        if self.request.user.is_authenticated():
            statuses = self.request.GET.get("status", "").split(",")
            if statuses:
                allowed_values = {
                    str(value) for value, _ in Elu._meta.get_field("status").choices
                }
                if all(status in allowed_values for status in statuses):
                    qs = qs.filter(status__in=[int(status) for status in statuses])

        department = self.request.GET.get("department", "tous")
        if department != "tous":
            qs = qs.filter(department=department)

        if "gender" in self.request.GET:
            qs = qs.filter(gender=self.request.GET["gender"])

        if "nuance_politique" in self.request.GET:
            qs = qs.filter(nuance_politique=self.request.GET["nuance_politique"])

        if "search" in self.request.GET:
            for word in self.request.GET["search"].split():
                qs = qs.filter(
                    Q(family_name__icontains=word)
                    | Q(city__icontains=word)
                    | Q(first_name__icontains=word)
                )

        assigned = self.request.GET.get("assigned")
        if assigned == "yes":
            qs = qs.filter(assigned_to__isnull=False)
        elif assigned == "no":
            qs = qs.filter(assigned_to__isnull=True)

        finished = self.request.GET.get("finished")
        if finished == "yes":
            qs = qs.filter(status__gte=Elu.STATUS_REFUSED)
        elif finished == "no":
            qs = qs.filter(status__lt=Elu.STATUS_REFUSED)

        sort_keys = []
        if "sort" in self.request.GET:
            sort = self.request.GET["sort"]
            if sort == "priority":
                sort_keys.append("priority")
            elif sort == "status":
                sort_keys.append("status")
            elif sort == "city":
                sort_keys.extend(
                    [Case(When(role="M", then=0), default=1), "role", "city"]
                )
        sort_keys.extend(["family_name", "first_name"])
        qs = qs.order_by(*sort_keys)

        qs = qs.annotate(Count("notes"))
        if "limit" in self.request.GET:
            qs = qs[: int(self.request.GET["limit"])]
        return qs


class EluDetailView(DetailView):
    queryset = Elu.objects.all()
    template_name = "elu-detail.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated():
            assigned_elu = self.request.COOKIES.get("assigned_elu")
            if str(assigned_elu) == str(context["object"].id):
                context["assigned"] = 1
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        self.object = self.get_object()
        action = request.POST.get("action")
        note = ""

        if action == "assign":
            if self.object.assigned_to != request.user:
                note = "Nouvelle assignation: {} → {}".format(
                    self.object.assigned_to or "", request.user
                )
                self.object.assigned_to = request.user
        elif action == "unassign":
            if self.object.assigned_to == request.user:
                note = "Nouvelle assignation: {} → {}".format(
                    self.object.assigned_to or "", "personne"
                )
                self.object.assigned_to = None
        elif action == "add_note":
            new_status = request.POST.get("status")
            if new_status:
                old_status = self.object.get_status_display()
                self.object.status = int(new_status)
                note = "Nouveau statut: {} → {}\n".format(
                    old_status, self.object.get_status_display()
                )
            note += request.POST.get("note", "")
        elif action == "update_contact":
            old_phone = self.object.private_phone
            old_email = self.object.private_email
            new_phone = request.POST.get("private_phone")
            new_email = request.POST.get("private_email")
            if old_phone != new_phone:
                note += "Nouveau téléphone privé: {} → {}\n".format(
                    old_phone, new_phone
                )
                self.object.private_phone = new_phone
            if old_email != new_email:
                note += "Nouvel email privé: {} → {}".format(old_email, new_email)
                self.object.private_email = new_email

        if note:
            self.object.save()
            self.object.notes.create(user=request.user, note=note)
        return HttpResponseRedirect(self.object.get_absolute_url())


class EluCSVForMap(View):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        qs = Elu.objects.exclude(city_latitude="").exclude(city_longitude="")
        status = request.GET.get("status", "")
        if status == "nothing-done":
            qs = qs.exclude(status__gte=Elu.STATUS_REFUSED).filter(
                Q(status=Elu.STATUS_NOTHING) & Q(assigned_to__isnull=True)
            )
        elif status == "done":
            qs = qs.filter(status__gte=Elu.STATUS_REFUSED)
        elif status == "in-progress":
            qs = qs.exclude(status__gte=Elu.STATUS_REFUSED).exclude(
                Q(status=Elu.STATUS_NOTHING) & Q(assigned_to__isnull=True)
            )
        elif status == "accepted":
            qs = qs.filter(status__gte=Elu.STATUS_ACCEPTED)
        department = request.GET.get("department")
        if department:
            deplist = department.split(",")
            qs = qs.filter(department__in=deplist)
        try:
            limit = request.GET.get("limit")
            if limit:
                qs = qs[: int(limit)]
        except:
            pass

        response = HttpResponse(content_type="text/plain", charset="utf-8")
        csvwriter = csv.writer(response)
        csvwriter.writerow(
            ["latitude", "longitude", "name", "phone", "email", "status", "url"]
        )
        for elu in qs:
            csvwriter.writerow(
                [
                    elu.city_latitude,
                    elu.city_longitude,
                    str(elu),
                    elu.public_phone,
                    elu.public_email,
                    elu.get_public_status_display(),
                    request.build_absolute_uri(elu.get_absolute_url()),
                ]
            )

        return response


class UserDetailView(DetailView):
    queryset = User.objects.all()
    template_name = "user-detail.html"
    slug_field = "username"
    slug_url_kwarg = "username"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        del context["user"]  # Avoid override of authenticated user
        if self.request.user.is_authenticated():
            context["assigned_elus"] = get_assigned_elus(
                self.get_object(), exclude_finished=False
            )
            context["departements"] = get_department_options(self.request)
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return HttpResponseForbidden()

        self.object = self.get_object()
        action = request.POST.get("action")

        if action == "update_profile":
            settings, _ = UserSettings.objects.get_or_create(user=self.request.user)
            settings.phone = request.POST.get("phone", "")
            settings.department = request.POST.get("department", "")
            settings.city = request.POST.get("city", "")
            settings.save()

        return HttpResponseRedirect(
            reverse("user-detail", args=[self.request.user.username])
        )


class DepartmentRankingView(TemplateView):
    template_name = "department-ranking.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        qs = Elu.objects.filter(status__gt=Elu.STATUS_NOTHING)
        qs = qs.values_list("department", "status")

        stats = {}
        for department, status in qs:
            dep_stats = stats.setdefault(
                department, {"department": department, "parrainages": 0, "contacts": 0}
            )
            dep_stats["contacts"] += 1
            if status >= Elu.STATUS_ACCEPTED:
                dep_stats["parrainages"] += 1
        result = list(stats.values())
        result.sort(key=lambda x: (x["parrainages"], x["contacts"]), reverse=True)
        context["classement_departments"] = result

        return context


class UserRankingView(TemplateView):
    template_name = "user-ranking.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Initialize user list with easy counts
        users = {}
        qs = User.objects.annotate(count_elus=Count("elu", distinct=True)).annotate(
            count_notes=Count("notes", distinct=True)
        )
        for user in qs:
            users[user.username] = {
                "username": user.username,
                "count_elus": user.count_elus,
                "count_notes": user.count_notes,
                "count_parrainages": 0,
                "user": user,
            }

        # Now add the number of parrainages
        qs = (
            Elu.objects.filter(
                status__gte=Elu.STATUS_ACCEPTED, assigned_to__isnull=False
            )
            .values_list("assigned_to__username")
            .annotate(count_parrainages=Count("id"))
        )
        for username, count in qs:
            users[username]["count_parrainages"] = count

        # Sort the result and return it
        classement_users = list(users.values())
        classement_users.sort(
            key=lambda x: (x["count_parrainages"], x["count_elus"], x["count_notes"]),
            reverse=True,
        )
        context["classement_users"] = classement_users
        return context


class DepartmentSynopticView(TemplateView):
    template_name = "department-synoptic.html"

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        stats = get_department_data()

        result = list(stats.values())
        result.sort(key=lambda x: x["display_department"])
        context["departments_data"] = result

        total = {}
        for key in result[0].keys():
            if not key.startswith("count_"):
                continue
            total[key] = sum(map(lambda x: x[key], result))
        context["total"] = total

        return context


class EluCSVForMailing(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("URL restricted to super-users")

        qs = (
            Elu.objects.filter(role="M")
            .exclude(Q(public_email="") & Q(private_email=""))
            .filter(status__lt=Elu.STATUS_REFUSED)
            .order_by("family_name", "first_name")
        )

        response = HttpResponse(content_type="text/plain", charset="utf-8")
        csvwriter = csv.writer(response)
        csvwriter.writerow(
            [
                "id",
                "email",
                "family_name",
                "first_name",
                "gender",
                "city_size",
                "civility",
                "small_city",
                "token",
            ]
        )
        for elu in qs:
            small_city = "N"
            if elu.city_size and elu.city_size <= 1000:
                small_city = "Y"
            csvwriter.writerow(
                [
                    elu.id,
                    elu.private_email or elu.public_email,
                    elu.family_name,
                    elu.first_name,
                    elu.gender,
                    elu.city_size if elu.city_size else "",
                    "Mme" if elu.gender == "F" else "M.",
                    small_city,
                    elu.private_token,
                ]
            )

        return response
