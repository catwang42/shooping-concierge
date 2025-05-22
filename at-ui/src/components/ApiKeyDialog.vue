<template>
    <v-dialog v-model="dialog" width="500">
        <v-card title="Enter Gemini API Key">
            <v-text-field label="Key:">
            </v-text-field>
            <v-btn text="Enter" variant="plain" @click="dialog = false">
            </v-btn>
        </v-card>
    </v-dialog>
</template>