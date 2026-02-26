<template>
  <PracticeExitConfirmModal
    :is-active="isActive"
    @confirm="$emit('confirm')"
    @cancel="$emit('cancel')"
  />
</template>

<script>
import PracticeExitConfirmModal from '../../components/PracticeExitConfirmModal.vue';

export default {
  name: 'ExitConfirmModal',
  components: {
    PracticeExitConfirmModal
  },
  props: {
    isActive: {
      type: Boolean,
      default: false
    }
  },
  emits: ['confirm', 'cancel']
};
</script>
