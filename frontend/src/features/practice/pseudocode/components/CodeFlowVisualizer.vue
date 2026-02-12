<template>
  <div class="code-flow-visualizer">
    <div class="header">
      <h3>Python Code Conversion Result</h3>
      <span v-if="score < 80" class="badge warning">Needs Improvement</span>
      <span v-else class="badge success">Excellent</span>
    </div>

    <div class="content">
      <div class="code-block">
        <pre><code class="language-python">{{ pythonCode }}</code></pre>
      </div>

      <div class="feedback-section" v-if="feedback">
        <h4>AI Feedback</h4>
        <p>{{ feedback }}</p>
      </div>
    </div>

    <div class="actions">
      <button @click="$emit('next')" class="btn-next">
        {{ score < 80 ? 'Solve Tail Question (+5pts)' : 'Start Deep Dive' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';

const props = defineProps({
  pythonCode: {
    type: String,
    default: '# No code generated'
  },
  score: {
    type: Number,
    required: true
  },
  feedback: {
    type: String,
    default: ''
  }
});

defineEmits(['next']);
</script>

<style scoped>
.code-flow-visualizer {
  background: #1e1e1e;
  border-radius: 8px;
  padding: 20px;
  color: #fff;
  border: 1px solid #333;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.badge.warning {
  background: #f59e0b;
  color: #000;
}

.badge.success {
  background: #10b981;
  color: #fff;
}

.code-block {
  background: #000;
  padding: 15px;
  border-radius: 6px;
  overflow-x: auto;
  font-family: 'Fira Code', monospace;
  margin-bottom: 20px;
  border: 1px solid #444;
}

.feedback-section {
  background: #2d2d2d;
  padding: 15px;
  border-radius: 6px;
  border-left: 4px solid #3b82f6;
}

.feedback-section h4 {
  margin: 0 0 5px 0;
  color: #3b82f6;
}

.btn-next {
  width: 100%;
  padding: 12px;
  margin-top: 20px;
  background: linear-gradient(90deg, #3b82f6, #2563eb);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  font-size: 1rem;
}

.btn-next:hover {
  opacity: 0.9;
}
</style>
