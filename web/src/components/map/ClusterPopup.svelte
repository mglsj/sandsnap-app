<script lang="ts">
	import {
		getSource,
		getMapContext,
	} from "svelte-maplibre/context.svelte.js";
	import type { Feature, Geometry } from "geojson";
	import type { GeoJSONSource } from "maplibre-gl";
	import type {
		ClusterProperties,
		SingleProperties,
	} from "./cluster_feature_properties.js";

	const { map } = $derived(getMapContext());
	const source = getSource();

	interface Props {
		feature: Feature<Geometry, ClusterProperties> | undefined;
	}

	let { feature }: Props = $props();

	let innerFeaturesPromise = $derived.by(async () => {
		if (!map || !source?.value || !feature) {
			return [];
		}

		const features = ((await (
			map.getSource(source.value) as GeoJSONSource
		)?.getClusterLeaves(feature.properties.cluster_id, 10000, 0)) ??
			[]) as Feature<Geometry, SingleProperties>[];

		features.sort((a, b) => {
			return b.properties.id - a.properties.id;
		});

		return features;
	});

	// Use this instead of an await template tag to avoid flickering
	let innerFeatures: Feature<Geometry, SingleProperties>[] = $state([]);

	$effect(() => {
		innerFeaturesPromise.then((f) => {
			innerFeatures = f;
		});
	});
</script>

<p>Sand Sizes</p>

{#each innerFeatures.slice(0, 10) as feat}
	<div class="text-sm">
		{feat.properties.id} :
		{#if feat.properties.size !== undefined}
			{feat.properties.size.toFixed(3)} mm
		{:else}
			Unprocessed
		{/if}
	</div>
{/each}
