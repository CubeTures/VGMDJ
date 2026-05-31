<script
	lang="ts"
	generics="T"
>
	import { PUBLIC_API_URL } from "$env/static/public";

	import { onDestroy, onMount } from "svelte";

	interface Props {
		endpoint: string;
		params?: URLSearchParams;
		onmessage: (data: T) => void;
	}

	let {
		endpoint,
		params = new URLSearchParams(),
		onmessage,
	}: Props = $props();

	let stream: EventSource | undefined;

	onMount(() => {
		stream = new EventSource(
			`${PUBLIC_API_URL}${endpoint}${params.toString()}`,
		);
		stream.onmessage = (event) => onmessage(event.data);
	});

	onDestroy(() => {
		stream?.close();
	});
</script>
