<script lang="ts">
	import { PUBLIC_API_URL } from "$env/static/public";
	import AsyncButton from "./AsyncButton.svelte";

	let files: FileList | undefined = $state();
	const file = $derived(files?.[0] ?? null);

	async function download() {
		const form: FormData = new FormData();
		form.append("file", file!);

		const res = await fetch(`${PUBLIC_API_URL}/download/csv`, {
			method: "POST",
			body: form,
		});
		return res.ok;
	}
</script>

<div
	class="bg-mauve-200 border border-mauve-400 rounded p-2 flex flex-col gap-2"
>
	<h2 class="font-bold text-lg">CSV</h2>
	<div class="grid grid-cols-[auto_1fr] gap-2 items-center">
		<label
			for="url"
			class="text-right">File</label
		>
		<input
			id="url"
			type="file"
			bind:files
			class="bg-mauve-50 rounded px-1 min-w-0"
		/>
	</div>
	<div class="flex justify-end">
		<AsyncButton onclick={download} />
	</div>
</div>
