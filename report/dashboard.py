from fasthtml.common import *
import matplotlib.pyplot as plt

# Import QueryBase, Employee, Team from employee_events
from employee_events import QueryBase, Employee, Team

# Import the load_model function from utils.py
from utils import load_model


"""
Below, we import the parent classes
you will use for subclassing.
"""
from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable,
)

from combined_components import FormGroup, CombinedComponent


# Create a subclass of base_components/dropdown
# called ReportDropdown
class ReportDropdown(Dropdown):

    def build_component(self, entity_id, model):
        # Set the dropdown label to the model name
        self.label = model.name.title()

        # Use the parent class to build the dropdown
        return super().build_component(entity_id, model)

    def component_data(self, entity_id, model):
        # Return names and IDs for employees or teams
        return model.names()


# Create a subclass of BaseComponent called Header
class Header(BaseComponent):

    def build_component(self, entity_id, model):
        return H1(model.name.title())


# Create a subclass of MatplotlibViz called LineChart
class LineChart(MatplotlibViz):

    def visualization(self, entity_id, model):
        # Query event counts for an employee or team
        data = model.event_counts(entity_id)

        # Replace missing values with zero
        data = data.fillna(0)

        # Use event_date as the DataFrame index
        data = data.set_index("event_date")

        # Sort dates in ascending order
        data = data.sort_index()

        # Convert daily event counts into cumulative totals
        data = data.cumsum()

        # Rename the positive and negative event columns
        data.columns = ["Positive", "Negative"]

        # Create the Matplotlib figure and axis
        fig, ax = plt.subplots()

        # Plot the cumulative event totals
        data.plot(ax=ax)

        # Apply black styling so the chart is visible
        self.set_axis_styling(
            ax,
            bordercolor="black",
            fontcolor="black",
        )

        # Set chart title and axis labels
        ax.set_title("Cumulative Performance Events", fontsize=20)
        ax.set_xlabel("Date")
        ax.set_ylabel("Cumulative Event Count")

        return fig


# Create a subclass of MatplotlibViz called BarChart
class BarChart(MatplotlibViz):

    # Load the machine-learning model once
    predictor = load_model()

    def visualization(self, entity_id, model):
        # Retrieve the input features for the ML model
        data = model.model_data(entity_id)

        # Calculate class probabilities
        probabilities = self.predictor.predict_proba(data)

        # Select the probability for the positive class
        probabilities = probabilities[:, 1]

        # Team model data contains one record per employee.
        # Display the team's average recruitment risk.
        if model.name == "team":
            pred = probabilities.mean()

        # Employee model data contains one record.
        else:
            pred = probabilities[0]

        # Create the Matplotlib horizontal bar chart
        fig, ax = plt.subplots()

        # Keep this code unchanged
        ax.barh([""], [pred])
        ax.set_xlim(0, 1)
        ax.set_title("Predicted Recruitment Risk", fontsize=20)

        # Apply visible axis styling
        self.set_axis_styling(
            ax,
            bordercolor="black",
            fontcolor="black",
        )

        return fig


# Create a CombinedComponent for the two visualizations
class Visualizations(CombinedComponent):

    children = [
        LineChart(),
        BarChart(),
    ]

    # Leave this line unchanged
    outer_div_type = Div(cls="grid")


# Create a DataTable subclass for employee/team notes
class NotesTable(DataTable):

    def component_data(self, entity_id, model):
        return model.notes(entity_id)


class DashboardFilters(FormGroup):

    id = "top-filters"
    action = "/update_data"
    method = "POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name="profile_type",
            hx_get="/update_dropdown",
            hx_target="#selector",
        ),
        ReportDropdown(
            id="selector",
            name="user-selection",
        ),
    ]


# Create the complete dashboard report
class Report(CombinedComponent):

    children = [
        Header(),
        DashboardFilters(),
        Visualizations(),
        NotesTable(),
    ]


# Initialize a FastHTML application
app = FastHTML()


# Initialize the Report class
report = Report()


# Root route displaying employee 1
@app.get("/")
def index():
    return report(1, Employee())


# Employee route, such as /employee/2
@app.get("/employee/{id}")
def employee(id: str):
    return report(id, Employee())


# Team route, such as /team/2
@app.get("/team/{id}")
def team(id: str):
    return report(id, Team())


# Keep the below code unchanged!
@app.get("/update_dropdown{r}")
def update_dropdown(r):
    dropdown = DashboardFilters.children[1]
    print("PARAM", r.query_params["profile_type"])

    if r.query_params["profile_type"] == "Team":
        return dropdown(None, Team())

    elif r.query_params["profile_type"] == "Employee":
        return dropdown(None, Employee())


@app.post("/update_data")
async def update_data(r):
    from fasthtml.common import RedirectResponse

    data = await r.form()
    profile_type = data._dict["profile_type"]
    id = data._dict["user-selection"]

    if profile_type == "Employee":
        return RedirectResponse(
            f"/employee/{id}",
            status_code=303,
        )

    elif profile_type == "Team":
        return RedirectResponse(
            f"/team/{id}",
            status_code=303,
        )


serve()