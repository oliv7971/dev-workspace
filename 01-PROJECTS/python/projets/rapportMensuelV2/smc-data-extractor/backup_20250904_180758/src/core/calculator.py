def calculate_periodic(data, month):
    # Logic to calculate periodic data for the given month
    last_in_month = data.get_last_in_month(month)
    last_before_month = data.get_last_before_month(month)
    
    if last_in_month is not None and last_before_month is not None:
        return last_in_month - last_before_month
    return None

def calculate_cumulative(data):
    # Logic to calculate cumulative data
    return data.get_last_global()

def process_measurements(measurements, month):
    results = []
    for measurement in measurements:
        periodic = calculate_periodic(measurement, month)
        cumulative = calculate_cumulative(measurement)
        results.append({
            'metric': measurement.metric,
            'periodic_mm': periodic,
            'cumulative_mm': cumulative,
            'date_last_in_month': measurement.get_date_last_in_month(month),
            'date_last_before_month': measurement.get_date_last_before_month(month),
            'date_last_global': measurement.get_date_last_global(),
            'cumul_out_of_month': measurement.is_cumul_out_of_month(),
            'duplicate_day': measurement.has_duplicate_day()
        })
    return results