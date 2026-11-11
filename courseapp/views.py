
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Course, Question, Choice, Enrollment, Submission


def course_details(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    return render(
        request,
        'courseapp/course_details_bootstrap.html',
        {'course': course}
    )


@login_required
def submit(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    if request.method != 'POST':
        return redirect('course_details', course_id=course.id)

    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user,
        course=course
    )

    submission = Submission.objects.create(
        enrollment=enrollment
    )

    for question in course.questions.all():
        selected_ids = request.POST.getlist(
            f'question_{question.id}'
        )

        valid_choices = Choice.objects.filter(
            id__in=selected_ids,
            question=question
        )

        submission.choices.add(*valid_choices)

    return redirect(
        'show_exam_result',
        course_id=course.id,
        submission_id=submission.id
    )


@login_required
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, id=course_id)

    submission = get_object_or_404(
        Submission,
        id=submission_id,
        enrollment__user=request.user,
        enrollment__course=course
    )

    questions = course.questions.all()
    selected_choices = submission.choices.all()

    selected_ids = list(
        selected_choices.values_list('id', flat=True)
    )

    total_grade = sum(
        question.grade for question in questions
    )

    total_score = sum(
        question.grade
        for question in questions
        if question.is_get_score(selected_ids)
    )

    percentage = (
        round((total_score / total_grade) * 100)
        if total_grade > 0 else 0
    )

    results = []

    for question in questions:
        selected_choice = selected_choices.filter(
            question=question
        ).first()

        results.append({
            'question': question,
            'selected_choice': selected_choice,
        })

    context = {
        'course': course,
        'submission': submission,
        'submissions': results,
        'choices': selected_choices,
        'score': total_score,
        'total': total_grade,
        'grade': percentage,
        'total_score': total_score,
        'total_grade': total_grade,
    }

    return render(
        request,
        'courseapp/exam_result.html',
        context
    )
