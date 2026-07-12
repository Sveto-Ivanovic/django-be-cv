<template>
  <div className="about-container">

        <div class="about-header-custom">
          <h1>About</h1>
          <p>
            A project exploring how AI systems can be built, tested, and improved
            using real-world evaluation workflows.
          </p>
        </div>

        <div class="about-grid">

          <div class="about-card">
            <h2>What is this?</h2>
            <p>
              This platform was created to experiment with AI infrastructure,
              model evaluation, and performance measurement. It allows users to
              connect models, test workflows, and compare results.
            </p>
          </div>

          <div class="about-card">
            <h2>What it does</h2>

            <ul>
              <li>Connect different AI models</li>
              <li>Upload benchmark datasets</li>
              <li>Evaluate model responses</li>
              <li>Compare accuracy and performance</li>
              <li>Work with embeddings and vector search</li>
            </ul>
          </div>

          <div class="about-card">
            <h2>Why I built it</h2>
            <p>
              This project demonstrates my interest in AI engineering,
              building practical tools, and understanding how modern AI
              applications are developed.
            </p>
          </div>

        </div>

        <div class="tech-section">
          <h2>Technology Focus</h2>

          <div class="tags">
            <span>LLM APIs</span>
            <span>RAG</span>
            <span>Embeddings</span>
            <span>Vector Databases</span>
            <span>AI Evaluation</span>
            <span>Web Development</span>
            <span>Django</span>
            <span>Vue.js</span>
          </div>
        </div>

      </div>
</template>




<script setup lang="ts">

</script>



<style scoped>
.about-page {
  padding: 80px 20px;
 
}

.about-container {
  max-width: 1100px;
  margin: auto;
}


.about-header-custom {
  text-align: center;
  margin-bottom: 60px;
   color: var(--hero-headline-color);
}


.about-header-custom  h1 {
  font-size: 52px;
  margin-bottom: 15px;
}


.about-header-custom p {
  max-width: 650px;
  margin: auto;
  font-size: 18px;
  line-height: 1.7;
}


.about-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 25px;
}


.about-card {
  border: 1px solid rgba(255,255,255,0.1);
  padding: 30px;
  border-radius: 20px;
  backdrop-filter: blur(12px);
  transition: 0.3s;
}


.about-card:hover {
  transform: translateY(-8px);
  border-color: #7c3aed;
}


.about-card h2 {
  margin-bottom: 15px;
  font-size: 22px;
  color: var(--hero-headline-color);

}


.about-card p,
.about-card li {
  color: var(--hero-headline-color);
  line-height: 1.7;
  opacity: 0.5;
}


.about-card ul {
  padding-left: 18px;
}


.tech-section {
  margin-top: 60px;
  text-align: center;
}


.tech-section h2 {
  margin-bottom: 25px;
}


.tags {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 15px;
}


.tags span {
  padding: 10px 18px;
  border-radius: 30px;
  border: 1px solid #374151;
  background-color: var(--button-background-color);
  color: var(--hero-headline-color);
  font-weight: 500;
}


@media(max-width:900px){

  .about-grid {
    grid-template-columns: 1fr;
  }

  .about-header h1 {
    font-size: 40px;
  }

}
</style>