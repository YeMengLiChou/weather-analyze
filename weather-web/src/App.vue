<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
	<router-view id="view_container" />
</template>

<style lang="css">
#view_container {
	width: 100%;
	height: 100%;
	padding: 0;
}

#app {
	width: 100vw;
	height: 100vh;
	max-width: none;
	display: block !important;
	margin: 0 auto !important;
	padding: 0 0 !important;
}

body {
	padding: 0;
	margin: 0;
	width: 100%;
	height: 100%;
	background-color: #2d3a4b;
}

html {
	padding: 0;
	margin: 0;
	height: 100%;
	box-sizing: border-box;
}
</style>
