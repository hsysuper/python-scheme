;;; Test Cases for the Scheme Project 

;; To run all tests:
;;     python3 scheme_test.py tests.scm
;;


;; The following should work for the initial files.

3
; expect 3

-123
; expect -123

1.25
; expect 1.25

#t
; expect #t

#f
; expect #f

;)
; expect Error

;; In the following sections, you should provide test cases, so that by 
;; running 
;;     python3 scheme_test.py tests.scm
;; you can test the portions of the project you've completed.  In fact, 
;; you might consider writing these tests BEFORE tackling the associated
;; problem!

; Problem 1  (the reader)
;   Initially, the project skeleton simply reads and prints the expressions
;   entered.  Later on, it starts evaluating them.  You may therefore need
;   to modify the tests you initially provide for this section when you get
;   to later sections.  For example, initially, entering the symbol x will
;   simply cause the evaluator to print "x" rather than attempting to evaluate
;   it (and getting an error).  Therefore, you may later have to modify
;   x to (e.g.) 'x

; YOUR TEST CASES HERE
#f
; expect #f

'(1 2 . 3)
; expect (1 2 . 3)

'(a b . c)
; expect (a b . c)

'(1 2 '(3 4))
; expect (1 2 (quote (3 4)))

; Problem A2 and B2 (symbol evaluation and simple defines)

; YOUR TEST CASES HERE

(define pi 3.14)
pi
; expect 3.14

(define x 15)
(define y x)
y
; expect 15

z
; expect Error


; Problem 3 (primitive function calls)

; YOUR TEST CASES HERE

(+ 2 3)
; expect 5

(quotient 1)
; expect Error

(+ 2 (* 4 5))
; expect 22

(+ x 5)
; expect 20

; Problem A4, B4, A5, B5, and 6 (calls on user-defined functions)

; YOUR TEST CASES HERE

(define (test-4 x y) (+ x y))
(test-4 5 6)
; expect 11

(define (test-5 x y . z) 
		(if (null? z) (+ x y) (max x y (car z)))
)
(test-5 1 2)
; expect 3
(test-5 2 3 4)
; expect 4
(test-5 2 3 4 5)
; expect 4

(define test-6 (lambda (x) (* x 2)))
(test-6 5)
; expect 10

(define test-7 (lambda () (lambda (x y) (+ x y))))
(define test-8 (test-7))
(test-8 5 11)
; expect 16



; Problem 7 (set!)

; YOUR TEST CASES HERE

x
; expect 15
(set! x 150)
x
; expect 150

(define (test-9 x) (set! x 250) x)
(test-9 x)
; expect 250
x
; expect 150


; Problem A8 (if, and)

; YOUR TEST CASES HERE

(define (test-10 x y)
		(if (and (> (+ x y) 10) (< (+ x y) 20)) 'Yes 'No)
)
(test-10 5 11)
; expect yes
(test-10 3 4)
; expect no
(test-10 66 44)
; expect no


; Problem B8 (cond, or)

; YOUR TEST CASES HERE
(define (test-11 x y) 
		(cond ((and (> (+ x y) 10) (< (+ x y) 20)) 'Yes)
			  ((or (< (+ x y) 10) (and (> (+ x y) 20) (< (+ x y) 40))))
		)
)

(test-11 5 6)
; expect Yes
(test-11 3 4)
; expect #t
(test-11 100 100)

(or (< 5 3) (> 6 4) (jeljflejflej))
; expect #t

(and (> 6 4) (< 5 3) (lefjlejflehfkehfkjhef))
; expect #f

(cond ((> 3 3) 'greater)
	  ((< 3 3) 'less)
	  (else 'equal)
)
; expect equal
(cond ((if (< -2 -3) #f -3) => abs)
	  (else #f)
)
; expect 3


; Problem 9 (let)

; YOUR TEST CASES HERE

(let ((x 25) (y (+ x 50))) (test-4 x y))
; expect 225

; Extra Credit 1 (let*)

; YOUR TEST CASES HERE

(let* ((x 25) (y (+ x 50))) (test-4 x y))
; expect 100


; Extra Credit 2 (case)

; YOUR TEST CASES HERE
(case (* 2 3)
	  ((2 3 5 7) 'prime)
	  ((1 4 6 8 9) 'composite)
)
; expect composite

(case (car '(a . b))
	  ((a c) 'd)
	  ((b 3) 'e))
; expect d

(case (car '(c d))
	  ((a e i o u) 'vowel)
	  ((w y) 'semivowel)
	  (else (define wohaha 15) 'consonant))
; expect consonant

wohaha
; expect 15

; Problem A10

;; pasted from behind because filter! can only run when reverse! is already defined.
(define (reverse! L)
  (define (inner_reverse! L previous)
    (cond ((null? L) L)
		  ((null? (cdr L))(set-cdr! L previous) L)
	      (else
                (define old-cdr (cdr L))
                (set-cdr! L previous)
                (inner_reverse! old-cdr L)
           )
    )
  )
  (inner_reverse! L '())
)



;; The subsequence of list S for which F outputs a true value (i.e., one
;; other than #f), computed destructively
(define (filter! f L)
   (define (inner-filter! L previous) 
		(cond ((null? L) L)
			  ((null? (cdr L)) (cond ((f (car L)) (set-cdr! L previous) L)
									 (else previous)
								)
				)
			  (else
					(define old-cdr (cdr L))
					(set-cdr! L previous)
					(cond ((f (car L)) (inner-filter! old-cdr L))
						  (else (inner-filter! old-cdr (cdr L))))
				)
		)
	)
	(reverse! (inner-filter! L '()))
)

(define (big x) (> x 5))

(define ints (list 1 10 3 8 4 7))
(define ints1 (cdr ints))

(define filtered-ints (filter! big ints))
filtered-ints
; expect (10 8 7)
(eq? filtered-ints ints1)
; expect #t


; Problem A11.

;; The number of ways to change TOTAL with DENOMS
;; At most MAX-COINS total coins can be used.
(define (count-change total denoms max-coins)
	(cond ((= max-coins 0) (if (= total 0) 1 0))
		  ((= total 0) 1)
		  ((< total 0) 0)
		  ((null? denoms) 0)
		  (else (+ 
				(count-change (- total (car denoms)) denoms (- max-coins 1))
				(count-change total (cdr denoms) max-coins)
				)
			)
	)
)


(define us-coins '(50 25 10 5 1))
(count-change 20 us-coins 18)
; expect 8

; Problem B10

;; Reverse list L destructively, creating no new pairs.  May modify the 
;; cdrs of the items in list L.
(define (reverse! L)
  (define (inner_reverse! L previous)
    (cond ((null? L) L)
		  ((null? (cdr L))(set-cdr! L previous) L)
	      (else
                (define old-cdr (cdr L))
                (set-cdr! L previous)
                (inner_reverse! old-cdr L)
           )
    )
  )
  (inner_reverse! L '())
)


(define L (list 1 2 3 4))
(define LR (reverse! L))
LR
; expect (4 3 2 1)

(eq? L (list-tail LR 3))
; expect #t

; Problem B11

;; The number of ways to partition TOTAL, where 
;; each partition must be at most MAX-VALUE
(define (count-partitions total max-value)
	(cond ((or (< total 0) (< max-value 1)) 0)
		  ((= total 0) 1)
		  (else (+ (count-partitions (- total max-value) max-value)(count-partitions total (- max-value 1))))
	)
)

(count-partitions 5 3)
; expect 5
; Note: The 5 partitions are [[3 2] [3 1 1] [2 2 1] [2 1 1 1] [1 1 1 1 1]]

; Problem 12

;; A list of all ways to partition TOTAL, where  each partition must 
;; be at most MAX-VALUE and there are at most MAX-PIECES partitions.
(define (list-partitions total max-pieces max-value)
	(define parts '())
	(define (inner-list-partitions  total max-pieces max-value sofar)
		(cond ((or (< total 0) (< max-value 1) (< max-pieces 0)))
			  ((= total 0) (set! parts (append parts (list sofar))))
			  (else (inner-list-partitions (- total max-value) (- max-pieces 1) max-value (append sofar (list max-value)))(inner-list-partitions total max-pieces (- max-value 1) sofar))
		)
	)
	(inner-list-partitions total max-pieces max-value '())
	parts
)

(list-partitions 5 2 4)
; expect ((4 1) (3 2))
(list-partitions 7 3 5)
; expect ((5 2) (5 1 1) (4 3) (4 2 1) (3 3 1) (3 2 2))