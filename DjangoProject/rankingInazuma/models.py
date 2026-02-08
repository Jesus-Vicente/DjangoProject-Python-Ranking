from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django_mongodb_backend.fields import ArrayField, ObjectIdAutoField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone

class UsuarioManager(BaseUserManager):
    def create_user(self, email, nombre, rol, password=None):
        if not email or not nombre:
            raise ValueError('Debes rellenar los campos requeridos (email, nombre)')
        email = self.normalize_email(email)
        usuario = self.model(email=email, nombre=nombre, rol=rol)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, nombre, rol='admin', password=None):
        usuario = self.create_user(email, nombre, rol, password)
        usuario.is_superuser = True
        usuario.is_staff = True
        usuario.save(using=self._db)
        return usuario

class Usuario(AbstractBaseUser, PermissionsMixin):
    id = ObjectIdAutoField(primary_key=True) # Campo obligatorio para MongoDB
    ROLES = (
        ('admin', 'Administrador'),
        ('usuario', 'Usuario'),
    )
    email = models.EmailField(unique=True)
    nombre = models.CharField(max_length=150, unique=True)
    rol = models.CharField(max_length=20, choices=ROLES, default='usuario')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'nombre'
    REQUIRED_FIELDS = ['email', 'rol']

    class Meta:
        db_table = 'usuarios'

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    code = models.IntegerField(null=False, unique=True)
    nombre = models.CharField(max_length=300)
    descripcion = models.CharField(max_length=300)
    logo = models.CharField(max_length=1000, blank=True, null=True)

    listaElementos = ArrayField(models.IntegerField(), blank=True, null=True, default=list)

    class Meta:
        db_table = 'categorias'
        managed = True

class Temporada(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    code = models.IntegerField(null=False, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.CharField(max_length=300)

    class Meta:
        db_table = 'temporadas'
        managed = True

    def __str__(self):
        return self.nombre

class Elemento(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    code = models.IntegerField(null=False, unique=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    categoriaCode = models.IntegerField(null=False)
    temporadaCode = models.IntegerField(null=False)

    posicion = models.CharField(max_length=50, blank=True, null=True)
    afinidad = models.CharField(max_length=50, blank=True, null=True)

    equipos = ArrayField(models.CharField(max_length=200), blank=True, null=True, default=list)

    imageUrl = models.CharField(max_length=1000)

    class Meta:
        db_table = 'elementos'
        managed = True

    def __str__(self):
        return self.nombre

class Equipos(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    code = models.IntegerField(null=False, unique=True)
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.CharField(max_length=300)

    imageUrl = models.CharField(max_length=1000)

    class Meta:
        db_table = 'equipos'
        managed = True

    def __str__(self):
        return self.nombre

class Reviews(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    usuario = models.CharField(max_length=150)
    elementoCode = models.IntegerField(null=False)
    puntuacion = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField()
    fecha = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'reviews'
        managed = True

    def __str__(self):
        return self.usuario + " " + str(self.puntuacion)

class Ranking(models.Model):
    id = ObjectIdAutoField(primary_key=True)
    usuario= models.CharField(max_length=150)
    categoriaCode = models.IntegerField(null=False)

    rankinLista = ArrayField(models.JSONField(), null=True, blank=True, default=list)

    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'rankings'
        managed = True

    def __str__(self):
        return f"{self.usuario} - Categoría: {self.categoriaCode}"