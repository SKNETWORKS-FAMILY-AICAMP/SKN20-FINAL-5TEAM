/**
 * Simple Rule-Based Evaluator for MVP
 * Checks if the user's input contains necessary keywords and logic.
 */
export const evaluateInternalLogic = (inputCode, level) => {
    const code = inputCode.toUpperCase();
    const feedbacks = [];
    let isSuccess = true;

    // 1. Basic Keyword Check
    if (level.solution_pattern) {
        level.solution_pattern.forEach(keyword => {
            if (!code.includes(keyword)) {
                isSuccess = false;
                feedbacks.push({
                    type: 'error',
                    message: `You are missing the keyword: "${keyword}"`
                });
            }
        });
    }

    // 2. Simple Heuristic Checks based on Difficulty
    if (level.input.includes("boolean") && !code.includes("IF")) {
        isSuccess = false;
        feedbacks.push({ type: 'warning', message: "Consider using an IF statement to check the boolean condition." });
    }

    if (level.goal.includes("Return") && !code.includes("RETURN")) {
        isSuccess = false;
        feedbacks.push({ type: 'error', message: "You need to RETURN a result." });
    }

    if (level.category === "Exceptions" && !code.includes("IF")) {
        // Assuming exceptions need checks
        feedbacks.push({ type: 'warning', message: "Did you check for the exception condition?" });
    }

    // Add positive feedback if empty
    if (isSuccess && feedbacks.length === 0) {
        feedbacks.push({ type: 'success', message: "Logic looks solid! Conditions appear to be handled." });
    } else if (!isSuccess && feedbacks.length === 0) {
        feedbacks.push({ type: 'error', message: "Something is missing, try reading the hint." });
    }

    return { success: isSuccess, feedbacks };
};

