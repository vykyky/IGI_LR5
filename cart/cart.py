from django.conf import settings
from main.models import Service

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, service, doctor, available_time):
        key = f"{service.id}:{doctor.id}:{available_time.id}"

        if key not in self.cart:
            self.cart[key] = {
                'service_id': service.id,
                'price': str(service.price),
                'doctor_id': doctor.id,
                'doctor_name': doctor.user.full_name,
                'time_id': available_time.id,
                'time_str': available_time.start_time.strftime("%d.%m %H:%M")
            }

        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, service):
        service_id = str(service.id)
        if service_id in self.cart:
            del self.cart[service_id]
            self.save()

    def __iter__(self):
        for key, item in self.cart.items():
            service = Service.objects.get(id=item['service_id'])
            item['service'] = service
            item['price'] = float(item['price'])
            item['total_price'] = item['price']  
            item['key'] = key
            yield item

    def __len__(self):
        return len(self.cart)

    def get_total_price(self):
        return sum(float(item['price']) for item in self.cart.values())

    def clear(self):
        del self.session[settings.CART_SESSION_ID]
        self.save()
