;;; Your entry for the Scheme contest
;;;
;;; Title: 
;;;   Le'vy's Lovers
;;;
;;; Description:
;;;   Windy dragon paths
;;;   Wistful lovers meet, but -- oh!
;;;   Wanderlust misleads
;;;
;;; Author:
;;;   Joey Moghadam
;;;   Siyuan (Jack) He

(exitonclick)

(define (even? x)
	(if (= 0 (modulo x 2)) #t #f)
)

(define (expo base power)
	(if (= power 0) 1 (* base (expo base (- power 1))))
)

(define (sine theta)
	(cond 	((= (modulo theta 360) 0) 0)
			((= theta 45) .707107)
			((= theta 90) 1)
			((= theta 135)  .707107)
			((= theta 180) 0)
			((= theta 225) (- .707107))
			((= theta 270) (- 1))
			((= theta 315) (- .707107))
			((= theta 360) 0)
			(else (display theta))
	)
)

(define (reduce-angle theta)
	(cond 	((and (> theta (- 1)) (< theta 361)) theta)
			((< theta 0) (reduce-angle (+ theta 360)))
			(else (reduce-angle (- theta 360)))
	)
)


(define (startposition level)
	(cond 	((= level 0) 1)
			((even? level) (expo 2 (- (/ level 2) 1)))
			(else(* .707107 (expo 2 (- (/ (+ level 1) 2) 1))))
	)
)

(define (twin-dragon level size)
	(hideturtle)
	(clear)
	(penup)
	(define xdistance (* size (startposition level)))
	(define ydistance 0)
	(setposition xdistance ydistance)
	(setheading 270)
	(define theta 270)
	(color 'pink)
	(define middle 0)
	(speed 0)
	(pendown)
	(define (draw-dragon level size)
		(define (other-dragon x1 y1 phi)
			(color 'blue)
			(penup)
			(setposition (- x1 ) y1)
			(setheading (- 360 phi))
			(pendown)
			(forward size)
			(backward size)
			(setheading phi)
			(penup)
			(setposition x1 y1)
			(color 'pink)
			(pendown)
		)
		(if (= middle 0) (set! middle level))
		(cond ((= level 0) 
				(other-dragon xdistance ydistance theta) 
				(forward size) 
				(set! xdistance (+ xdistance (* size (sine (reduce-angle theta)))))
				(set! ydistance (+ ydistance (* size (sine (reduce-angle (- 90 theta))))))
				)
			(else 	
				(right 45)
				(set! theta (reduce-angle (+ theta 45)))
				(draw-dragon (- level 1) size)
				(if (= middle level) (draw-heart size theta))
				(left 90)
				(set! theta (reduce-angle (- theta 90)))
				(draw-dragon (- level 1) size)
				(right 45)
				(set! theta (reduce-angle (+ theta 45)))
			)	
		)
	)
	(draw-dragon level size)
)
(define (draw-heart size heading)
(color 'red)
(setheading 45)
(begin_fill)
(forward size)
(circle (/ size 2) 180)
(setheading 315)
(circle (/ size 2) 180)
(forward size)
(end_fill)
(setheading heading)
)

;try variant calls to twin-dragon for different levels of detail
;(twin-dragon 7 15)
;(twin-dragon 8 15) 
;(twin-dragon 9 10)
(twin-dragon 11 5)
;(twin-dragon 12 4) 