<script lang="ts">
	import { onMount } from "svelte";
	import Dialog from "./Dialog.svelte";
	import { PUBLIC_API_URL } from "$env/static/public";
	import AsyncButton from "./AsyncButton.svelte";

	let dialog: HTMLDialogElement | undefined = $state(undefined);
	let time: number | undefined = $state(undefined);

	onMount(() => {
		load();
	});

	async function load() {
		const res = await fetch(`${PUBLIC_API_URL}/auto-hide`, {
			headers: { "Content-Type": "application/json" },
		});
		const json = await res.json();
		time = json["auto_hide_time"];
	}

	async function save() {
		const res = await fetch(`${PUBLIC_API_URL}/auto-hide`, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(time),
		});
		return res.ok;
	}
</script>

<!-- svelte-ignore a11y_interactive_supports_focus -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
	class="bg-mauve-200 border border-mauve-400 rounded p-2 flex justify-between"
	onclick={() => dialog?.showModal()}
>
	<p>Automatic Hide</p>
	{#if time === undefined}
		<pre>...</pre>
	{:else}
		<pre>{time}s</pre>
	{/if}
	<Dialog bind:dialog>
		<div class="p-2 flex gap-2">
			<input
				bind:value={time}
				type="number"
				class="text-center"
			/>
			<div>
				<AsyncButton onclick={save} />
			</div>
		</div>
	</Dialog>
</div>
