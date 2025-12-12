<script lang="ts">
	import * as Sidebar from "$lib/components/ui/sidebar";
	import IconBeach from "@tabler/icons-svelte/icons/beach";
</script>

<Sidebar.Menu>
	<Sidebar.MenuItem>
		<Sidebar.MenuButton class="data-[slot=sidebar-menu-button]:p-1.5!">
			{#snippet child({ props })}
				<a href="/" {...props}>
					<IconBeach class="size-6!" />
					<span class="text-base font-semibold">Sand Snap</span>
				</a>
			{/snippet}
		</Sidebar.MenuButton>
	</Sidebar.MenuItem>
</Sidebar.Menu>
