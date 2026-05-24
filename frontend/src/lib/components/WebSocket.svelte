<script
	lang="ts"
	generics="T"
>
	import { PUBLIC_API_URL } from "$env/static/public";

	import { onDestroy, onMount } from "svelte";

	interface Props {
		endpoint: string;
		params?: URLSearchParams;
		messages?: T[];
		value?: T;
	}

	let {
		endpoint,
		params = new URLSearchParams(),
		messages = $bindable([]),
		value = $bindable(),
	}: Props = $props();

	let socket: WebSocket | undefined;

	function onMessage(event: MessageEvent<T>) {
		messages.push(event.data);
		value = event.data;
	}

	onMount(() => {
		socket = new WebSocket(
			`${PUBLIC_API_URL.replace("http://", "ws://")}${endpoint}/${params.toString()}`,
		);
		socket.onmessage = onMessage;
	});

	onDestroy(() => {
		socket?.close();
	});
</script>
