import simpy
import random
import enum
from typing import Optional, Generator, NamedTuple
import homeModel as hm
from environment import TimeSlotEnvironment
from utils import truncnorm
from numpy import average


class InhabitantState(enum.Enum):
    SLEEPS = "Sleeps"
    WAKES_UP = "Wakes up"
    PREPARES_TO_LEAVE = "Prepares to leave"
    LEFT = "Left"
    ARRIVES = "Arrives"
    RELAXES = "Relaxes"
    READS = "Reads"
    WORKS = "Works"   # Work at home
    DOES_HOBBY = "Does hobby" # Each inhabitant has its own hobby
    PREPARES_FOOD = "Prepares food"
    EATS = "Eats"
    TAKES_SHOWER = "Takes shower"
    GOES_TO_SLEEP = "Goes to sleep"
    UNKNOWN = "UNKNOWN"

class stateEnd(NamedTuple):
    min: float | None
    max: float | None

class Inhabitant:
    '''Inhabitant of the house. Has its own schedule and behavior.

    ..._state() methods correspond to a particular state (actions/intercations).
    ..._behavior() methods correspond to transitions between states.
    current_state_actions() is called in ..._behavior() methods to execute the current state.

    Inherit this class to create a custom inhabitant.
    '''
    def __init__(self, 
                 env:TimeSlotEnvironment, 
                 home: Optional[hm.Home] = None, 
                 initial_state: InhabitantState = InhabitantState.UNKNOWN) -> None:
        self.env: TimeSlotEnvironment = env
        self.state: InhabitantState = initial_state
        self.home: hm.Home = home if home else hm.Home(env)
        self.stateMethodMap = {
            InhabitantState.SLEEPS: self.sleeps_state,
            InhabitantState.WAKES_UP: self.wakes_up_state,
            InhabitantState.PREPARES_TO_LEAVE: self.prepares_to_leave_state,
            InhabitantState.LEFT: self.left_state,
            InhabitantState.ARRIVES: self.arrives_state,
            InhabitantState.RELAXES: self.relaxes_state,
            InhabitantState.READS: self.reads_state,
            InhabitantState.WORKS: self.works_state,
            InhabitantState.DOES_HOBBY: self.does_hobby_state,
            InhabitantState.PREPARES_FOOD: self.prepares_food_state,
            InhabitantState.EATS: self.eats_state,
            InhabitantState.TAKES_SHOWER: self.takes_shower_state,
            InhabitantState.GOES_TO_SLEEP: self.goes_to_sleep_state,
            InhabitantState.UNKNOWN: self.unknown_state
        }
        self.stateEnd: stateEnd = stateEnd(None, None)

    def sleeps_state(self) -> Generator[simpy.Event, None, None]:
        yield self.env.timeout(1)

    def wakes_up_state(self) -> Generator[simpy.Event, None, None]:
        yield self.env.timeout(1)

    def prepares_to_leave_state(self) -> Generator[simpy.Event, None, None]:
        yield self.env.timeout(1)

    def left_state(self) -> Generator[simpy.Event, None, None]:
        yield self.env.timeout(1)

    def arrives_state(self) -> Generator[simpy.Event, None, None]:
        yield self.env.timeout(1)

    def relaxes_state(self) -> Generator[simpy.Event, None, None]:
        yield self.env.timeout(1)

    def reads_state(self) -> Generator[simpy.Event, None, None]:
        yield self.env.timeout(1)

    def works_state(self) -> Generator[simpy.Event, None, None]:
        yield self.env.timeout(1)

    def does_hobby_state(self) -> Generator[simpy.Event, None, None]:
        yield self.env.timeout(1)

    def prepares_food_state(self) -> Generator[simpy.Event, None, None]:
        yield self.env.timeout(1)

    def eats_state(self) -> Generator[simpy.Event, None, None]:
        yield self.env.timeout(1)

    def takes_shower_state(self) -> Generator[simpy.Event, None, None]:
        yield self.env.timeout(1)

    def goes_to_sleep_state(self) -> Generator[simpy.Event, None, None]:
        yield self.env.timeout(1)

    def unknown_state(self):
        raise ValueError(f'Tried to execute unknown state {self.state}!')


    def current_state_actions(self) -> Generator[simpy.Event, None, None]:
        # Current state event generator
        stateYield = self.stateMethodMap.get(self.state, self.unknown_state)()

        # State events
        if self.stateEnd.min != None:
            # States are cut short if they are too long
            while self.env.now < self.stateEnd.min:
                try:
                    yield next(stateYield)
                except StopIteration:
                    # States are extended if they are too short
                    
                    # end = random.uniform(self.stateEnd.min, self.stateEnd.max) if self.stateEnd.max else self.stateEnd.min
                    end = truncnorm(average(self.stateEnd), 1, self.stateEnd.min, self.stateEnd.max) if self.stateEnd.max else self.stateEnd.min
                    yield self.env.timeout(end - self.env.now)

            if self.stateEnd.max and self.env.now > self.stateEnd.max:
                raise ValueError(f'Current state {self.state} event took too long!\nState ended: {self.env.now}\nEnd interval: {self.stateEnd}')
        else:
            yield from stateYield

    def workday_behavior(self) -> Generator[simpy.Event, None, None] | None:
        yield self.env.timeout(1)

    def weekend_behavior(self) -> Generator[simpy.Event, None, None] | None:
        yield self.env.timeout(1)


    def behaviour(self):
        weekendBehavior = False
        workdayBehavior = False
        while True:
            currentState = self.state
            if self.env.is_weekend():
                eventGenerator = self.weekend_behavior()
                weekendBehavior = True
            else:
                eventGenerator = self.workday_behavior()
                workdayBehavior = True
            
            if eventGenerator:
                yield from eventGenerator

            # # Current state actions
            # # (if state changed or if behavior changed)
            # if currentState != self.state:
            #     yield from self.current_state_actions()
            # elif weekendBehavior and workdayBehavior:
            #     yield from self.current_state_actions()
            #     weekendBehavior, workdayBehavior = False, False
            # else:
            #     # Await next state change
            #     yield self.env.timeout(1)

            # Current state actions
            yield from self.current_state_actions()