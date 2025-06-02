from django.shortcuts import render, redirect, \
    get_object_or_404
from django.views.decorators.http import require_POST
from main.models import Service, DoctorSchedule, Appointment
from .cart import Cart
from .forms import CartAddServiceForm
from users.models import *
from django.contrib import messages

import logging
logger = logging.getLogger('myapp')

@require_POST
def cart_add(request, service_id):
    logger.debug(f"Attempt to add service {service_id} to cart ")
    cart = Cart(request)
    service = get_object_or_404(Service, id=service_id)
    form = CartAddServiceForm(request.POST, service=service)

    if form.is_valid():
        cd = form.cleaned_data
        doctor = cd['doctor']
        available_time = cd['available_time']
        cart.add(
                service=service,
                doctor=doctor,
                available_time=available_time
            )
        logger.info(f"Service {service_id} added to cart by user {request.user.id } "
                       f"with doctor {doctor.id} and time {available_time}")
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, key):
    logger.debug(f"Attempt to remove item {key} from cart by user {request.user.id }")
    cart = Cart(request)
    if key in cart.cart:
        del cart.cart[key]
        cart.save()
        logger.info(f"Item {key} removed from cart by user {request.user.id }")
    return redirect('cart:cart_detail')


def cart_detail(request):
    logger.debug(f"Cart detail viewed by user {request.user.id}")
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})

def make_order(request):
    logger.info(f"Attempt to make order by user {request.user.id}")
    cart = Cart(request)
    logger.debug(f"Cart contains {len(cart)} items for order processing")
    try:
        client = Client.objects.get(user=request.user)
        logger.debug(f"Client found: {client.id}")
    except Client.DoesNotExist:
        logger.error(f"User {request.user.id} is not registered as client")
        messages.error(request, "Ошибка: вы не зарегистрированы как клиент.")
        return redirect('main:home')

    used_schedule_ids = set()
    skipped_conflicts = []
    skipped_taken = []

    appointments_to_create = []  

    for item in cart:
        doctor = Doctor.objects.get(id=item['doctor_id'])
        service = item['service']
        schedule_id = item['time_id']
        schedule = DoctorSchedule.objects.get(id=schedule_id)
        logger.debug(f"Processing item: service {service.id}, doctor {doctor.id}, schedule {schedule_id}")

        if schedule_id in used_schedule_ids:
            skipped_conflicts.append(f"{schedule} — конфликт внутри корзины")
            logger.warning("cart conflict")
            continue

        if Appointment.objects.filter(scheduled_time=schedule).exists():
            skipped_taken.append(f"{schedule} — уже занят")
            logger.warning("cart taken")
            continue

        appointments_to_create.append({
            'user': client,
            'doctor': doctor,
            'service': service,
            'scheduled_time': schedule
        })

        used_schedule_ids.add(schedule_id)
        logger.debug(f"Item added to creation list: service {service.id}, doctor {doctor.id}, schedule {schedule_id}")

    if skipped_conflicts or skipped_taken:
        message = "❌ Заказ не оформлен, обнаружены проблемы:\n"
        if skipped_conflicts:
            message += "\nКонфликты внутри корзины:\n" + "\n".join(skipped_conflicts)
        if skipped_taken:
            message += "\nУже занятые слоты (пока лежали в корзине):\n" + "\n".join(skipped_taken)

        logger.warning(f"Order failed for user {request.user.id} due to: "
                         f"{len(skipped_conflicts)} conflicts, {len(skipped_taken)} taken slots")
        messages.error(request, message)
        return redirect('cart:cart_detail')

    for data in appointments_to_create:
        Appointment.objects.create(**data)
        logger.debug(f"Appointment created")

    cart.clear()
    logger.info(f"Order successfully created by user {request.user.id}")
    messages.success(request, "✅ Вы успешно записались на все выбранные услуги.")
    return redirect('cart:cart_detail')