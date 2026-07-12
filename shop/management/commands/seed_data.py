from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from shop.models import Category, Product, Order, OrderItem

User = get_user_model()


class Command(BaseCommand):
    help = 'Popola il database con dati demo per il progetto E-commerce API'

    def handle(self, *args, **options):
        self.stdout.write('Creazione utenti demo...')

        customer, _ = User.objects.get_or_create(
            username='customer_demo',
            defaults={'role': User.Role.CUSTOMER, 'email': 'customer@demo.com'}
        )
        customer.set_password('cust12345')
        customer.save()

        manager, _ = User.objects.get_or_create(
            username='manager_demo',
            defaults={'role': User.Role.STORE_MANAGER, 'email': 'manager@demo.com'}
        )
        manager.set_password('manager12345')
        manager.save()

        self.stdout.write('Creazione categorie...')
        elettronica, _ = Category.objects.get_or_create(
            name='Elettronica', defaults={'description': 'Dispositivi e accessori elettronici'}
        )
        libri, _ = Category.objects.get_or_create(
            name='Libri', defaults={'description': 'Libri di ogni genere'}
        )
        casa, _ = Category.objects.get_or_create(
            name='Casa', defaults={'description': 'Articoli per la casa'}
        )

        self.stdout.write('Creazione prodotti...')
        prodotti_data = [
            ('Tastiera meccanica', 'Tastiera meccanica RGB', Decimal('59.90'), 15, elettronica),
            ('Mouse wireless', 'Mouse ergonomico wireless', Decimal('24.90'), 30, elettronica),
            ('Monitor 24"', 'Monitor Full HD 24 pollici', Decimal('149.00'), 8, elettronica),
            ('Il Nome della Rosa', 'Romanzo di Umberto Eco', Decimal('12.50'), 20, libri),
            ('Clean Code', 'Manuale di programmazione', Decimal('34.90'), 12, libri),
            ('Lampada da tavolo', 'Lampada LED regolabile', Decimal('19.90'), 25, casa),
            ('Set pentole', 'Set di 5 pentole antiaderenti', Decimal('79.90'), 6, casa),
        ]
        prodotti = []
        for name, desc, price, stock, cat in prodotti_data:
            p, _ = Product.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'price': price, 'stock': stock, 'category': cat}
            )
            prodotti.append(p)

        self.stdout.write('Creazione ordine di esempio...')
        if not Order.objects.filter(user=customer).exists():
            order = Order.objects.create(user=customer, status=Order.Status.PAID)
            OrderItem.objects.create(
                order=order, product=prodotti[0], quantity=1,
                price_at_purchase=prodotti[0].price
            )
            OrderItem.objects.create(
                order=order, product=prodotti[3], quantity=2,
                price_at_purchase=prodotti[3].price
            )

        self.stdout.write(self.style.SUCCESS('Dati demo creati con successo!'))
        self.stdout.write('---')
        self.stdout.write('Account demo:')
        self.stdout.write('  customer_demo / cust12345 (Customer)')
        self.stdout.write('  manager_demo / manager12345 (Store Manager)')