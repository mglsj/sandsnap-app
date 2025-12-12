<script lang="ts">
	import type { Feature, Geometry } from "geojson";
	import type { GeoJSONSource } from "maplibre-gl";
	import type {
		ClusterProperties,
		SingleProperties,
	} from "./cluster_feature_properties.js";

	interface Props {
		feature: Feature<Geometry, SingleProperties> | undefined;
	}

	let { feature }: Props = $props();
</script>

{#if feature}
	<div class="p-2">
		<img
			src={feature.properties.image}
			alt="Sample"
			decoding="async"
			loading="lazy"
			class="h-auto w-auto object-contain max-w-64 max-h-64 mb-2"
		/>
		<h3 class="font-bold mb-2">Feature Details</h3>
		<ul>
			<li><strong>ID:</strong> {feature.properties.id}</li>
			<li>
				<strong>Size:</strong>
				{feature.properties.size.toFixed(3)} mm
			</li>
		</ul>
	</div>
{:else}
	<div class="p-2">
		<p>No feature data available.</p>
	</div>
{/if}
