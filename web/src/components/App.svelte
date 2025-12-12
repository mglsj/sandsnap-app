<script lang="ts">
	import * as Sidebar from "$lib/components/ui/sidebar";
	import Data from "./data/Data.svelte";
	import Map from "./map/Map.svelte";
	import AppSidebar from "./sidebar/AppSidebar.svelte";
	import SiteHeader from "./ui/SiteHeader.svelte";

	interface Props {
		path?: string;
	}

	const { path = "/" }: Props = $props();
</script>

<main>
	<Sidebar.Provider>
		<AppSidebar variant="inset" />

		<Sidebar.Inset>
			{#if path === "/"}
				<SiteHeader title="Home" />
				<Map />
			{:else if path === "/data/"}
				<SiteHeader title="Data" />
				<Data />
			{:else}
				<SiteHeader title="Not Found" />
				<p class="p-4">Page not found.</p>
			{/if}
		</Sidebar.Inset>
	</Sidebar.Provider>
</main>
