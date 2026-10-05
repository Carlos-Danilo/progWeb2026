from decimal import Decimal

from django.test import TestCase
from django.contrib.auth.models import User

from loja.models import Carrinho, CarrinhoItem, Favorito, Produto


class AuthenticationViewTests(TestCase):
    def test_login_page_displays_form(self):
        response = self.client.get('/login')

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth/auth.html')
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')

    def test_login_with_valid_credentials(self):
        User.objects.create_user(username='cliente', password='Senha123!segura')

        response = self.client.post('/login', {
            'username': 'cliente',
            'password': 'Senha123!segura',
        })

        self.assertRedirects(response, '/')
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_redirects_to_requested_page(self):
        User.objects.create_user(username='cliente', password='Senha123!segura')

        response = self.client.post('/login?next=/produto/edit/1', {
            'username': 'cliente',
            'password': 'Senha123!segura',
        })

        self.assertRedirects(response, '/produto/edit/1')

    def test_login_rejects_external_next_url(self):
        User.objects.create_user(username='cliente', password='Senha123!segura')

        response = self.client.post(
            '/login?next=https://evil.example/',
            {
                'username': 'cliente',
                'password': 'Senha123!segura',
            },
            HTTP_HOST='localhost',
        )

        self.assertRedirects(response, '/')

    def test_product_edit_requires_login_and_preserves_next_url(self):
        response = self.client.get('/produto/edit/1')

        self.assertRedirects(
            response,
            '/login?next=/produto/edit/1',
        )

    def test_logout_ends_session_and_redirects_to_login(self):
        User.objects.create_user(username='cliente', password='Senha123!segura')
        self.client.login(username='cliente', password='Senha123!segura')

        response = self.client.get('/logout')

        self.assertRedirects(response, '/login')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_navigation_menu_changes_for_authenticated_user(self):
        visitor_response = self.client.get('/')

        self.assertContains(visitor_response, 'Registrar')
        self.assertNotContains(visitor_response, 'Editar Perfil')

        User.objects.create_user(username='cliente', password='Senha123!segura')
        self.client.login(username='cliente', password='Senha123!segura')
        user_response = self.client.get('/')

        self.assertContains(user_response, 'Perfil')
        self.assertContains(user_response, 'Editar Perfil')
        self.assertContains(user_response, 'Sair')
        self.assertNotContains(user_response, 'Registrar')

    def test_login_with_invalid_credentials_shows_message(self):
        response = self.client.post('/login', {
            'username': 'cliente',
            'password': 'senha-incorreta',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dados de usuário incorretos')

    def test_register_creates_user(self):
        response = self.client.post('/register', {
            'username': 'novo-cliente',
            'email': 'cliente@example.com',
            'password': 'Senha123!segura',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Conta criada com sucesso!')
        user = User.objects.get(username='novo-cliente')
        self.assertEqual(user.email, 'cliente@example.com')
        self.assertTrue(user.check_password('Senha123!segura'))

    def test_register_rejects_existing_username(self):
        User.objects.create_user(
            username='cliente',
            email='existente@example.com',
            password='Senha123!segura',
        )

        response = self.client.post('/register', {
            'username': 'cliente',
            'email': 'novo@example.com',
            'password': 'Senha123!segura',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Já existe um usuário com este username!')

    def test_register_rejects_invalid_email(self):
        response = self.client.post('/register', {
            'username': 'novo-cliente',
            'email': 'email-invalido',
            'password': 'Senha123!segura',
        })

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            'novo-cliente',
            User.objects.values_list('username', flat=True),
        )


class CartViewTests(TestCase):
    def setUp(self):
        self.product = Produto.objects.create(
            Produto='Produto de teste',
            preco=Decimal('12.50'),
        )

    def test_add_product_creates_session_cart(self):
        response = self.client.get(f'/carrinho/{self.product.id}')

        self.assertRedirects(response, '/carrinho/')
        cart = Carrinho.objects.get(pk=self.client.session['carrinho_id'])
        item = CarrinhoItem.objects.get(carrinho=cart, produto=self.product)
        self.assertEqual(item.quantidade, 1)
        self.assertEqual(item.preco, Decimal('12.50'))

    def test_adding_same_product_increments_quantity_and_total(self):
        self.client.get(f'/carrinho/{self.product.id}')
        response = self.client.get(f'/carrinho/{self.product.id}')

        self.assertRedirects(response, '/carrinho/')
        cart = Carrinho.objects.get(pk=self.client.session['carrinho_id'])
        item = CarrinhoItem.objects.get(carrinho=cart, produto=self.product)
        self.assertEqual(item.quantidade, 2)
        self.assertEqual(cart.total, Decimal('25.00'))

    def test_cart_page_lists_items(self):
        self.client.get(f'/carrinho/{self.product.id}')

        response = self.client.get('/carrinho/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Produto de teste')
        self.assertContains(response, 'R$ 12,50')

    def test_remove_item_only_removes_item_from_session_cart(self):
        self.client.get(f'/carrinho/{self.product.id}')
        cart = Carrinho.objects.get(pk=self.client.session['carrinho_id'])
        item = CarrinhoItem.objects.get(carrinho=cart, produto=self.product)

        response = self.client.post(f'/carrinho/remover/{item.id}/')

        self.assertRedirects(response, '/carrinho/')
        self.assertFalse(CarrinhoItem.objects.filter(pk=item.id).exists())

    def test_cannot_remove_item_from_another_cart(self):
        own_cart = Carrinho.objects.create()
        other_cart = Carrinho.objects.create()
        self.client.session['carrinho_id'] = own_cart.id
        item = CarrinhoItem.objects.create(
            carrinho=other_cart,
            produto=self.product,
            quantidade=1,
            preco=self.product.preco,
        )

        response = self.client.post(f'/carrinho/remover/{item.id}/')

        self.assertEqual(response.status_code, 404)
        self.assertTrue(CarrinhoItem.objects.filter(pk=item.id).exists())

    def test_confirm_cart_requires_login_and_records_order(self):
        self.client.get(f'/carrinho/{self.product.id}')
        cart_id = self.client.session['carrinho_id']

        response = self.client.get('/carrinho/confirmar')

        self.assertRedirects(
            response,
            '/login?next=/carrinho/confirmar',
        )
        user = User.objects.create_user(
            username='comprador',
            password='Senha123!segura',
        )
        self.client.force_login(user)
        response = self.client.get('/carrinho/confirmar')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Compra Confirmada')
        cart = Carrinho.objects.get(pk=cart_id)
        self.assertEqual(cart.user, user)
        self.assertEqual(cart.situacao, 1)
        self.assertIsNotNone(cart.confirmado_em)
        self.assertEqual(cart.total, Decimal('12.50'))
        self.assertNotIn('carrinho_id', self.client.session)
        self.assertContains(response, 'Produto de teste')
        self.assertContains(response, 'R$ 12,50')

    def test_confirming_empty_cart_does_not_create_order(self):
        self.client.force_login(
            User.objects.create_user(
                username='comprador',
                password='Senha123!segura',
            )
        )

        response = self.client.get('/carrinho/confirmar')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Seu carrinho está vazio')
        self.assertEqual(Carrinho.objects.count(), 0)

    def test_cart_quantity_buttons_increase_and_decrease_quantity(self):
        self.client.get(f'/carrinho/{self.product.id}')
        cart = Carrinho.objects.get(pk=self.client.session['carrinho_id'])
        item = CarrinhoItem.objects.get(carrinho=cart, produto=self.product)

        response = self.client.post(f'/carrinho/item/{item.id}/aumentar')
        self.assertRedirects(response, '/carrinho/')
        item.refresh_from_db()
        self.assertEqual(item.quantidade, 2)

        response = self.client.post(f'/carrinho/item/{item.id}/diminuir')
        self.assertRedirects(response, '/carrinho/')
        item.refresh_from_db()
        self.assertEqual(item.quantidade, 1)

        self.client.post(f'/carrinho/item/{item.id}/diminuir')
        item.refresh_from_db()
        self.assertEqual(item.quantidade, 1)


class FavoriteViewTests(TestCase):
    def setUp(self):
        self.product = Produto.objects.create(
            Produto='Produto favorito',
            preco=Decimal('8.75'),
        )

    def test_home_page_has_buy_and_favorite_actions(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Comprar', html=False)
        self.assertContains(response, 'Favoritar', html=False)
        self.assertContains(response, f'/carrinho/{self.product.id}')
        self.assertContains(response, f'/carrinho/favoritos/adicionar/{self.product.id}/')

    def test_buy_button_from_home_adds_product_to_session_cart(self):
        response = self.client.get(f'/carrinho/{self.product.id}')

        self.assertRedirects(response, '/carrinho/')
        cart = Carrinho.objects.get(pk=self.client.session['carrinho_id'])
        self.assertTrue(
            CarrinhoItem.objects.filter(carrinho=cart, produto=self.product).exists()
        )

    def test_favoriting_requires_login_and_is_completed_after_login(self):
        url = f'/carrinho/favoritos/adicionar/{self.product.id}/'
        response = self.client.get(url)

        self.assertRedirects(response, f'/login?next={url}')
        user = User.objects.create_user(
            username='favorito',
            password='Senha123!segura',
        )
        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Deseja favoritar Produto favorito?')
        response = self.client.post(url)

        self.assertRedirects(response, '/carrinho/favoritos/')
        self.assertTrue(
            Favorito.objects.filter(user=user, produto=self.product).exists()
        )

    def test_favorite_add_is_idempotent_and_user_scoped(self):
        user = User.objects.create_user(
            username='favorito',
            password='Senha123!segura',
        )
        self.client.force_login(user)
        url = f'/carrinho/favoritos/adicionar/{self.product.id}/'
        self.client.post(url)
        self.client.post(url)

        self.assertEqual(Favorito.objects.filter(user=user).count(), 1)
        response = self.client.get('/carrinho/favoritos/')
        self.assertContains(response, 'Produto favorito')
        self.assertContains(response, 'R$ 8,75')

        another_user = User.objects.create_user(
            username='outro',
            password='Senha123!segura',
        )
        self.client.force_login(another_user)
        response = self.client.get('/carrinho/favoritos/')
        self.assertContains(response, 'Você ainda não favoritou produtos.')
        self.assertNotContains(response, 'Produto favorito')

    def test_favorite_can_be_removed(self):
        user = User.objects.create_user(
            username='favorito',
            password='Senha123!segura',
        )
        Favorito.objects.create(user=user, produto=self.product)
        self.client.force_login(user)

        response = self.client.post(
            f'/carrinho/favoritos/remover/{self.product.id}/'
        )

        self.assertRedirects(response, '/carrinho/favoritos/')
        self.assertFalse(Favorito.objects.filter(user=user).exists())

    def test_favorites_list_requires_login(self):
        response = self.client.get('/carrinho/favoritos/')

        self.assertRedirects(response, '/login?next=/carrinho/favoritos/')
