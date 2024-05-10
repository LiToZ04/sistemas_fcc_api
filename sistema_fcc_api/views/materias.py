from django.shortcuts import render
from django.db.models import *
from django.db import transaction
from sistema_fcc_api.serializers import *
from sistema_fcc_api.models import *
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.generics import CreateAPIView, DestroyAPIView, UpdateAPIView
from rest_framework import permissions
from rest_framework import generics
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from django.core import serializers
from django.utils.html import strip_tags
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
import string
import random
import json

class MateriasAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request):
        # Obtener las materias de la base de datos
        materias_queryset = Materias.objects.all()

        # Serializar las materias
        materias = MateriaSerializer(materias_queryset, many=True).data 

        return Response(materias)

class MateriasView(APIView):
    def get(self, request, *args, **kwargs):
        materia = get_object_or_404(Materias, id = request.GET.get("id"))
        materia = MateriaSerializer(materia, many=False).data 
        materia["dias_json"] = json.loads(materia["dias_json"])
        return Response(materia, 200)
    
    def post(self, request):
        data = request.data
        dias_json = data.get('dias_json', [])
        
        if not dias_json:
            return Response({'dias_json': ['REQUERIDO']}, status=status.HTTP_400_BAD_REQUEST)

        # Convertir el array dias_json a una cadena JSON
        data['dias_json'] = json.dumps(dias_json)

        serializer = MateriaSerializer(data=data) 

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MateriasViewEdit(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    def put(self, request, *args, **kwargs):
        # iduser=request.data["id"]
        materia = get_object_or_404(Materias, id=request.data["id"])
        materia.nrc = request.data["nrc"]
        materia.nombre_materia = request.data["nombre_materia"]
        materia.dias_json = json.dumps(request.data["dias_json"])
        materia.hora_inicial = request.data["hora_inicial"]
        materia.hora_final = request.data["hora_final"]
        materia.salon = request.data["salon"]
        materia.programa_educativo = request.data["programa_educativo"]
        materia.save()
    
        serializer = MateriaSerializer(materia, many=False).data 

        return Response(serializer,200)  

    def delete(self, request, *args, **kwargs):
        materia = get_object_or_404(Materias, id=request.GET.get("id"))
        try:
            materia.delete()
            return Response({"details":"Materia eliminada"},200)
        except Exception as e:
            return Response({"details":"Algo pasó al eliminar"},400)   