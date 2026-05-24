<script lang="ts">
	import type { DownloadStatusMessage } from "$lib/types";
	import WebSocket from "./WebSocket.svelte";

	let messages: DownloadStatusMessage[] = $state([]);
</script>

<WebSocket
	endpoint="/download-status"
	bind:messages
/>
