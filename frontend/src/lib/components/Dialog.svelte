<script lang="ts">
	import type { Snippet } from "svelte";

	interface Props {
		dialog?: HTMLDialogElement;
		children: Snippet;
	}

	let { dialog = $bindable(), children }: Props = $props();
</script>

<dialog
	class="m-auto rounded"
	bind:this={dialog}
	onclick={(e) => {
		if (e.target == dialog) {
			e.stopPropagation();
			dialog?.close();
		}
	}}
>
	{@render children()}
</dialog>
