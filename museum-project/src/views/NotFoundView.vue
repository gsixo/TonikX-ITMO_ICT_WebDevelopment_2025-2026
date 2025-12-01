<template>
  <v-container class="fill-height">
    <v-row class="fill-height" align="center" justify="center">
      <v-col cols="12" md="6" class="text-center">
        <v-icon color="primary" size="80">mdi-compass-off</v-icon>
        <div class="text-h4 mt-4 mb-2">Страница не найдена</div>
        <p class="text-body-1 mb-6">
          К сожалению, нужный раздел не существует или был перемещён.
        </p>
        <v-btn color="primary" :to="{ name: 'dashboard' }">
          На главную
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

