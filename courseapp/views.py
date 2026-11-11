from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Question, Submission, Choice


def course_details(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, 'courseapp/course_details_bootstrap.html', {
        'course': course
    })


@login_required
def submit(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        Submission.objects.filter(
            user=request.user,
            question__course=course
        ).delete()

        for question in course.questions.all():
            choice_id = request.POST.get(f'question_{question.id}')

            if choice_id:
                choice = get_object_or_404(
                    Choice, id=choice_id, question=question
                )
                Submission.objects.create(
                    user=request.user,
                    question=question,
                    selected_choice=choice
                )

        return redirect('show_exam_result', course_id=course.id)

    return redirect('course_details', course_id=course.id)


@login_required
def show_exam_result(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    submissions = Submission.objects.filter(
        user=request.user,
        question__course=course
    ).select_related('question', 'selected_choice')

    total = course.questions.count()
    score = sum(
        1 for submission in submissions
        if submission.selected_choice.is_correct
    )

    return render(request, 'courseapp/exam_result.html', {
        'course': course,
        'submissions': submissions,
        'score': score,
        'total': total
    })