<template>
    <div class="tutorial-page">

        <div class="tutorial-hero">
            <h1 class="tutorial-title">How this app works</h1>
            <p class="tutorial-subtitle">
                A short guide to building a retrieval pipeline: get your documents into a vector store, then
                measure how well that store answers real questions.
            </p>
        </div>

        <div class="form-section">
            <h3 class="section-title">The big picture</h3>
            <p class="tutorial-text">
                There are three pages in this app, and they map to two stages of a Retrieval-Augmented
                Generation (RAG) workflow:
            </p>

            <n-steps :current="0" vertical class="tutorial-steps">
                <n-step title="1. Embed into Pinecone">
                    <template #default>
                        Turn raw text or PDFs into vectors and store them in a Pinecone index, so they can later
                        be searched by meaning.
                    </template>
                </n-step>
                <n-step title="2. Embed into Supabase">
                    <template #default>
                        The same idea, but storing your vectors in a Supabase namespace instead of Pinecone. Use
                        whichever vector store you prefer, or both.
                    </template>
                </n-step>
                <n-step title="3. Evaluate Benchmark">
                    <template #default>
                        Ask a set of questions against a vector store you built in step 1 or 2, and score how good
                        the retrieved answers are, using an LLM as the judge.
                    </template>
                </n-step>
            </n-steps>

            <n-alert type="info" class="tutorial-alert">
                Steps 1 and 2 are about <strong>building</strong> a searchable knowledge base. Step 3 is about
                <strong>grading</strong> one. You always need to embed data before you can evaluate it.
            </n-alert>
        </div>

        <div class="form-section">
            <h3 class="section-title">Before you start</h3>
            <p class="tutorial-text">
                Every page checks your profile for the API keys it needs, and blocks the Submit button until
                they're set. You'll see a red warning banner at the top of a page if something is missing.
            </p>
            <ul class="tutorial-list">
                <li><strong>Embed key</strong> (Gemini, Cohere, or Jina) &mdash; required on all three pages, used
                    to turn text into vectors.</li>
                <li><strong>Pinecone key</strong> &mdash; required only on the Pinecone page.</li>
                <li><strong>LLM key</strong> (Gemini, Groq, or Mistral) &mdash; required only on the Evaluate
                    Benchmark page, used to answer and grade questions.</li>
            </ul>
            <p class="tutorial-text">
                Add these from your <a class="tutorial-link" @click="defineNavigate('Profile')">Profile</a> page
                first.
            </p>
        </div>

        <div class="form-section">
            <h3 class="section-title">Page by page</h3>

            <n-collapse arrow-placement="right" class="tutorial-collapse">

                <n-collapse-item title="Embed into Pinecone" name="pinecone">
                    <p class="tutorial-text">
                        Use this page to load documents into a Pinecone index so you can search them later.
                    </p>
                    <ul class="tutorial-list">
                        <li><strong>Embed Model</strong> &mdash; which embedding model turns your text into
                            vectors. The dropdown only shows models you have an API key for.</li>
                        <li><strong>Use Existing Index</strong> &mdash; pick the Pinecone index your vectors will
                            be written to. Indexes are created ahead of time from your Pinecone account or via button <code>+ Create Index</code> on the page Pinecone Indexes.</li>
                        <li><strong>Include Lexical Index</strong> &mdash; turn this on if you also want keyword
                            (BM25-style) search alongside semantic search, then choose the lexical index to pair
                            with it. This enables <em>hybrid search</em> later, in the Evaluate step.</li>
                        <li><strong>Chunking</strong> &mdash; long documents are split into smaller pieces before
                            embedding. If enabled, set a <strong>Chunk Size</strong> (minimum 300) and a
                            <strong>Chunk Overlap</strong> so meaning isn't lost at chunk boundaries.</li>
                        <li><strong>Input Data</strong> &mdash; either:
                            <ul class="tutorial-sublist">
                                <li><strong>text</strong>: paste a JSON array, either plain strings or
                                    <code>{ text, metadata }</code> objects (see the info icon next to the field
                                    for the exact format), or</li>
                                <li><strong>file</strong>: upload up to 5 PDFs directly.</li>
                            </ul>
                        </li>
                    </ul>
                    <p class="tutorial-text">
                        Hit Submit and the app chunks (if enabled), embeds, and writes everything into the index
                        you selected.
                    </p>
                </n-collapse-item>

                <n-collapse-item title="Embed into Supabase" name="supabase">
                    <p class="tutorial-text">
                        The Supabase page mirrors the Pinecone page, but organizes vectors into a
                        <strong>namespace</strong> rather than an index, and doesn't have a separate lexical
                        store &mdash; keyword search is handled within the same namespace.
                    </p>
                    <ul class="tutorial-list">
                        <li><strong>Embed Model</strong> &mdash; same idea as on the Pinecone page.</li>
                        <li><strong>Select Namespace</strong> &mdash; either pick an existing namespace, or
                            create a <strong>New Namespace</strong> by typing a name at least 8 characters long.
                        </li>
                        <li><strong>Chunking</strong> &mdash; identical to the Pinecone page: optional chunk size
                            (minimum 300) and overlap.</li>
                        <li><strong>Input Data</strong> &mdash; the same two modes as Pinecone: pasted JSON
                            (strings, or <code>{ text, metadata }</code> objects) or PDF file upload.</li>
                    </ul>
                    <p class="tutorial-text">
                        Submit embeds your data and writes it into that namespace, ready to be queried in the
                        evaluation step.
                    </p>
                </n-collapse-item>

                <n-collapse-item title="Evaluate Benchmark" name="evaluate">
                    <p class="tutorial-text">
                        This page measures retrieval quality: it runs a list of questions against a vector store
                        you already built, then uses an LLM to grade how good the answers were.
                    </p>
                    <ul class="tutorial-list">
                        <li><strong>Input Testcase Name</strong> &mdash; a label (8+ characters) so you can find
                            this evaluation run again later.</li>
                        <li><strong>QA Model</strong> &mdash; the LLM that answers each question using the
                            retrieved chunks.</li>
                        <li><strong>Evaluation Model</strong> &mdash; the LLM that grades the QA model's answers.
                            It can be the same model as QA, or a different, stronger one for a more objective
                            score.</li>
                        <li><strong>Vector Store Settings</strong> &mdash; choose <strong>Supabase</strong> or
                            <strong>Pinecone</strong>, then:
                            <ul class="tutorial-sublist">
                                <li>pick the namespace or index you embedded data into earlier,</li>
                                <li>set <strong>Top K</strong>, the number of chunks retrieved per question,</li>
                                <li>set <strong>Mode</strong>: <code>semantic</code> (meaning-based),
                                    <code>lexical</code> (keyword-based), or <code>hybrid</code> (both combined)
                                    &mdash; lexical and hybrid require a lexical index/namespace to exist,</li>
                                <li>for Supabase, also choose a <strong>Semantic Search Mode</strong>
                                    (cosine, euclidean, or inner product) to define how similarity is
                                    measured.</li>
                            </ul>
                        </li>
                        <li><strong>Fetch Neighbor Settings</strong> &mdash; optionally pull in chunks that sit
                            near each retrieved chunk (e.g. adjacent pages or list items), which can give the QA
                            model more surrounding context. Configure how many neighboring chunks and
                            pages/array members to include, or fetch all of them.</li>
                        <li><strong>Input Data</strong> &mdash; a JSON array of questions, either just
                            <code>question</code>, or <code>question</code> plus a <code>reference_answer</code>
                            for every item (you can't mix the two within one run), or upload a JSON file with the
                            same structure.</li>
                    </ul>
                    <p class="tutorial-text">
                        Submit and the app retrieves context for each question, generates an answer, grades it,
                        and stores the results under the testcase name you gave it.
                    </p>
                </n-collapse-item>

            </n-collapse>
        </div>

        <div class="form-section">
            <h3 class="section-title">A typical first run</h3>
            <ol class="tutorial-ordered-list">
                <li>Add your Embed, Pinecone/Supabase, and LLM API keys on the Profile page.</li>
                <li>Go to <strong>Embed into Pinecone</strong> or <strong>Embed into Supabase</strong>, pick an
                    embed model and index/namespace, and submit your text or PDFs.</li>
                <li>Go to <strong>Evaluate Benchmark</strong>, point it at the same index/namespace, give it a
                    list of questions, and submit.</li>
                <li>Compare results across testcases as you try different chunk sizes, top K values, or search
                    modes, to see what retrieval setup answers your questions best.</li>
            </ol>
        </div>

    </div>
</template>

<script setup lang="ts">
import { NSteps, NStep, NAlert, NCollapse, NCollapseItem } from 'naive-ui'
import { useRouter } from 'vue-router';

const router = useRouter()

function defineNavigate(name: string){
    router.push({ name: name })
}

</script>

<style scoped>
.tutorial-page {
    max-width: 860px;
    margin: 0 auto;
    padding: 24px 16px 64px;
}

.tutorial-hero {
    margin-bottom: 32px;
}

.tutorial-title {
    font-size: 28px;
    font-weight: 700;
    margin: 0 0 8px;
}

.tutorial-subtitle {
    font-size: 15px;
    opacity: 0.75;
    margin: 0;
}

.tutorial-text {
    line-height: 1.6;
    margin: 0 0 12px;
}

.tutorial-list,
.tutorial-ordered-list {
    line-height: 1.7;
    padding-left: 20px;
    margin: 0 0 12px;
}

.tutorial-sublist {
    margin-top: 4px;
    padding-left: 18px;
}

.tutorial-steps {
    margin: 16px 0;
}

.tutorial-alert {
    margin-top: 16px;
}

.tutorial-collapse {
    margin-top: 8px;
}

.tutorial-link {
    cursor: pointer;
    text-decoration: underline;
}

code {
    background: rgba(128, 128, 128, 0.15);
    padding: 1px 5px;
    border-radius: 4px;
    font-size: 0.9em;
}
</style>