<script lang="ts">
	import IconMap from "@tabler/icons-svelte/icons/map";
	import IconDatabase from "@tabler/icons-svelte/icons/database";

	import * as Sidebar from "$lib/components/ui/sidebar";
	import type { ComponentProps } from "svelte";
	import Nav from "./Nav.svelte";
	import NavHeader from "./NavHeader.svelte";

	const data = {
		nav: [
			{
				title: "Map",
				url: "/",
				icon: IconMap,
			},
			{
				title: "Data",
				url: "/data",
				icon: IconDatabase,
			},
		],
	};

	let {
		ref = $bindable(null),
		collapsible = "icon",
		...restProps
	}: ComponentProps<typeof Sidebar.Root> = $props();
</script>

<Sidebar.Root {collapsible} {...restProps}>
	<!-- Header -->
	<Sidebar.Header>
		<NavHeader />
	</Sidebar.Header>

	<!-- Content -->
	<Sidebar.Content>
		<Nav items={data.nav} class="mt-auto" />
	</Sidebar.Content>

	<!-- Footer -->
	<Sidebar.Footer></Sidebar.Footer>
</Sidebar.Root>
