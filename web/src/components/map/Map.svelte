<script lang="ts">
	import {
		MapLibre,
		GeoJSON,
		CircleLayer,
		SymbolLayer,
		Popup,
		hoverStateFilter,
	} from "svelte-maplibre";
	import type { Feature, Geometry } from "geojson";
	import type {
		ClusterProperties,
		SingleProperties,
	} from "./cluster_feature_properties";
	import ClusterPopup from "./ClusterPopup.svelte";
	import SinglePopup from "./SinglePopup.svelte";
</script>

<MapLibre
	style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
	class="relative h-full w-full"
	standardControls
>
	<GeoJSON
		id="earthquakes"
		data={"/data.geojson"}
		cluster={{
			radius: 50,
			maxZoom: 14,
			properties: {
				total_size: ["+", ["get", "size"]],
			},
		}}
	>
		<CircleLayer
			id="cluster_circles"
			applyToClusters
			hoverCursor="pointer"
			paint={{
				// Use step expressions (https://maplibre.org/maplibre-gl-js-docs/style-spec/#expressions-step)
				// with three steps to implement three types of circles:
				//   * Blue, 20px circles when point count is less than 100
				//   * Yellow, 30px circles when point count is between 100 and 750
				//   * Pink, 40px circles when point count is greater than or equal to 750
				"circle-color": [
					"step",
					["get", "point_count"],
					"#51bbd6",
					100,
					"#f1f075",
					750,
					"#f28cb1",
				],
				"circle-radius": [
					"step",
					["get", "point_count"],
					20,
					100,
					30,
					750,
					40,
				],
				"circle-stroke-color": "#f00",
				"circle-stroke-width": 1,
				"circle-stroke-opacity": hoverStateFilter(0, 1),
			}}
			manageHoverState
		>
			<Popup openOn="click">
				{#snippet children({
					data,
				}: {
					data: Feature<Geometry, ClusterProperties> | undefined;
				})}
					<ClusterPopup feature={data ?? undefined} />
				{/snippet}
			</Popup>
		</CircleLayer>

		<SymbolLayer
			id="cluster_labels"
			interactive={false}
			applyToClusters
			layout={{
				"text-field": [
					"format",
					["get", "point_count_abbreviated"],
					{},
					"\n",
					{},
					[
						"number-format",
						["/", ["get", "total_size"], ["get", "point_count"]],
						{
							"max-fraction-digits": 2,
						},
					],
					{ "font-scale": 0.8 },
				],
				"text-size": 12,
				"text-offset": [0, -0.1],
			}}
		/>

		<CircleLayer
			id="earthquakes_circle"
			applyToClusters={false}
			hoverCursor="pointer"
			paint={{
				"circle-color": "#11b4da",
				"circle-radius": 6,
				"circle-stroke-width": 1,
				"circle-stroke-color": "#fff",
			}}
		>
			<Popup openOn="click">
				{#snippet children({
					data,
				}: {
					data: Feature<Geometry, SingleProperties> | undefined;
				})}
					<SinglePopup feature={data ?? undefined} />
				{/snippet}
			</Popup>
		</CircleLayer>
	</GeoJSON>
</MapLibre>
