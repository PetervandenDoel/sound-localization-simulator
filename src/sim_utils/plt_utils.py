import matplotlib.pyplot as plt
import matplotlib.lines as lines
import numpy as np
from sim_utils.common_types import cyl_to_cart, polar_to_cart2d, CylindricalPosition
import global_vars

def plot_calculated_positions(position_list, initial_guess, sigma):
    '''
    plots the 2D graph showing the pinger position, hydrophone position,
    pinger initial guess, and calculated position distribution
    '''
    hx = [cyl_to_cart(pos).x for pos in global_vars.hydrophone_positions]
    hy = [cyl_to_cart(pos).y for pos in global_vars.hydrophone_positions]
    #x and y are 1 element lists
    x  = [polar_to_cart2d(pos).x for pos in position_list]
    y  = [polar_to_cart2d(pos).y for pos in position_list]
    
    #creating x and y values for phi at a large distance
    position_list_far = [CylindricalPosition(100, position_list[0].phi, position_list[0].z)]
    x1  = [polar_to_cart2d(pos).x for pos in position_list_far]
    y1  = [polar_to_cart2d(pos).y for pos in position_list_far]

    px = cyl_to_cart(global_vars.pinger_position).x
    py = cyl_to_cart(global_vars.pinger_position).y
    gx = polar_to_cart2d(initial_guess).x
    gy = polar_to_cart2d(initial_guess).y

    f, (ax1, ax2) = plt.subplots(1, 2, figsize=(10,5))

    h = ax1.hist2d(hx, hy, bins=40, range=[[-5e-2, 5e-2], [-5e-2, 5e-2]])
    ax1.set_xlabel("x (m)")
    ax1.set_ylabel("y (m)")
    ax1.set_title("Hydrophone XY Distribution")
    f.colorbar(h[3], ax=ax1)

    #h = ax2.hist2d([40], [40], density=True, range=[[-50, 50], [-50, 50]], bins=40)
    ax2.scatter(hx, hy, label="Hydrophones", c = 'white')
    ax2.scatter(px, py, label="Pinger", c='orange')
    #2d has no initial guess
    #ax2.scatter(gx, gy, label="Initial Guess", c = 'red')
    ax2.add_line(lines.Line2D([0, x1[0]], [0, y1[0]], alpha = 0.5, linewidth=5.0, label="1D Localization Angle Estimate", c="yellow"))
    ax2.set_xlabel("x (m)")
    ax2.set_ylabel("y (m)")
    sigma_string = r'$\sigma = $' + str(round(sigma, 2))
    ax2.set_title("Distribution for Pinger Position Results %s" % sigma_string)

    #changes to make up for removing yellow box
    ax2.set_xlim(left=-50, right=50)
    ax2.set_ylim(bottom=-50, top=50)
    ax2.set_facecolor("#440154")

    ax2.legend(loc='lower left')
    f.colorbar(h[3], ax=ax2)

def plot_signals(*signals, title="Hydrophone Signals"):
    plt.figure()
    i=0
    for signal in signals:
        plt.plot(signal, label="hydrophone %0d"%i)
        i += 1
    plt.title(title)
    plt.legend()

def plt_param_sweep_abs_avg_error(param_vals, actual_vals_dict,
                                  sim_results_dict, title, ispolar=False, 
                                  scaley=1, scalex=1, isangular_error=False):

    error_dict = _get_error_dict(actual_vals_dict, sim_results_dict, 
                                 isangular_error)
    param_vals = np.array(param_vals)
    
    fig = plt.figure()
    if ispolar:
        ax = fig.add_subplot(111, projection='polar')
    else:
        ax = fig.add_subplot(111)
    
    for key, errors in error_dict.items():
        ax.plot(param_vals*scalex, errors*scaley, label=key)
    
    plt.title(title)
    plt.legend()
    plt.show()

def _get_error_dict(actual_vals_dict, sim_results_dict, isangular_error):
    keys = actual_vals_dict.keys()
    error_dict = {key:[] for key in keys}
    
    for key in keys:
        actual_vals = actual_vals_dict[key]
        sim_results = sim_results_dict[key]
        
        average_errors = []
        for actual, result in zip(actual_vals, sim_results):
            if isangular_error:
                # convert to range 0->2pi before finding the error
                error = [
                    np.abs((actual)%(2*np.pi)-(calculated)%(2*np.pi)) 
                    for calculated in result
                ]
            else:
                error = [np.abs(actual-calculated) for calculated in result]
            average_errors.append(sum(error)/len(error))
        error_dict[key] = np.array(average_errors)

    return error_dict
